import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import settings
from sensor_manager import SensorMode, manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

scheduler = AsyncIOScheduler()

# 벌크 전송 대상 센서 (여러 건의 데이터를 모아서 배열로 전송)
BULK_SENSORS = {"SN-SEOUL-001", "SN-BUSAN-002", "SN-JEJU-003"}


def _get_bulk_count(serial_number: str) -> int:
    """NORMAL 모드 + 벌크 대상이면 BULK_COUNT, 그 외에는 단일 전송"""
    sensor = manager.sensors.get(serial_number)
    if sensor and sensor.mode == SensorMode.EMERGENCY:
        return 1
    return settings.BULK_COUNT if serial_number in BULK_SENSORS else 1


def _add_sensor_job(serial_number: str):
    interval = manager.get_interval(serial_number)
    bulk_count = _get_bulk_count(serial_number)
    scheduler.add_job(
        manager.send_data,
        "interval",
        seconds=interval,
        args=[serial_number, bulk_count],
        id=serial_number,
        replace_existing=True,
    )


def _reschedule_sensor_job(serial_number: str):
    # 모드 변경 시 bulk_count도 바뀌므로 잡을 재생성
    _add_sensor_job(serial_number)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await manager.register_all()
    # 등록 직후 즉시 첫 데이터 전송
    for sn in manager.sensors:
        bulk_count = settings.BULK_COUNT if sn in BULK_SENSORS else 1
        await manager.send_data(sn, bulk_count)
    for sn in manager.sensors:
        _add_sensor_job(sn)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="IoT Sensor Simulator", lifespan=lifespan)


# --- Schemas ---

class ModeUpdate(BaseModel):
    mode: SensorMode


class BrokenUpdate(BaseModel):
    broken: bool


class SensorOut(BaseModel):
    serial_number: str
    mode: SensorMode
    broken: bool
    bulk: bool


# --- Routes ---

@app.get("/sensors", response_model=list[SensorOut])
async def list_sensors():
    return [
        SensorOut(
            serial_number=s.serial_number,
            mode=s.mode,
            broken=s.broken,
            bulk=s.serial_number in BULK_SENSORS,
        )
        for s in manager.sensors.values()
    ]


@app.patch("/sensors/{serial_number}/mode", response_model=SensorOut)
async def change_mode(serial_number: str, body: ModeUpdate):
    ok = await manager.change_mode(serial_number, body.mode, sync_backend=False)
    if not ok:
        raise HTTPException(404, f"센서 {serial_number}을(를) 찾을 수 없습니다")
    _reschedule_sensor_job(serial_number)
    s = manager.sensors[serial_number]
    return SensorOut(
        serial_number=s.serial_number,
        mode=s.mode,
        broken=s.broken,
        bulk=s.serial_number in BULK_SENSORS,
    )


@app.patch("/sensors/{serial_number}/broken", response_model=SensorOut)
async def set_broken(serial_number: str, body: BrokenUpdate):
    ok = manager.set_broken(serial_number, body.broken)
    if not ok:
        raise HTTPException(404, f"센서 {serial_number}을(를) 찾을 수 없습니다")
    s = manager.sensors[serial_number]
    return SensorOut(
        serial_number=s.serial_number,
        mode=s.mode,
        broken=s.broken,
        bulk=s.serial_number in BULK_SENSORS,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SENSOR_PORT)
