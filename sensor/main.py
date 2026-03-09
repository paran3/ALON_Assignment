import logging
from contextlib import asynccontextmanager
from enum import Enum

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import settings
from sensor_manager import SensorMode, manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

scheduler = AsyncIOScheduler()


def _add_sensor_job(serial_number: str):
    interval = manager.get_interval(serial_number)
    scheduler.add_job(
        manager.send_data,
        "interval",
        seconds=interval,
        args=[serial_number],
        id=serial_number,
        replace_existing=True,
    )


def _reschedule_sensor_job(serial_number: str):
    interval = manager.get_interval(serial_number)
    scheduler.reschedule_job(serial_number, trigger="interval", seconds=interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await manager.register_all()
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


# --- Routes ---

@app.get("/sensors", response_model=list[SensorOut])
async def list_sensors():
    return [
        SensorOut(serial_number=s.serial_number, mode=s.mode, broken=s.broken)
        for s in manager.sensors.values()
    ]


@app.patch("/sensors/{serial_number}/mode", response_model=SensorOut)
async def change_mode(serial_number: str, body: ModeUpdate):
    ok = await manager.change_mode(serial_number, body.mode)
    if not ok:
        raise HTTPException(404, f"센서 {serial_number}을(를) 찾을 수 없습니다")
    _reschedule_sensor_job(serial_number)
    s = manager.sensors[serial_number]
    return SensorOut(serial_number=s.serial_number, mode=s.mode, broken=s.broken)


@app.patch("/sensors/{serial_number}/broken", response_model=SensorOut)
async def set_broken(serial_number: str, body: BrokenUpdate):
    ok = manager.set_broken(serial_number, body.broken)
    if not ok:
        raise HTTPException(404, f"센서 {serial_number}을(를) 찾을 수 없습니다")
    s = manager.sensors[serial_number]
    return SensorOut(serial_number=s.serial_number, mode=s.mode, broken=s.broken)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SENSOR_PORT)
