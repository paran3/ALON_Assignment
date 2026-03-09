import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.core.exceptions import SensorAlreadyExistsError, SensorNotFoundError
from app.crud import create_sensor, get_all_sensors, get_sensor, update_sensor_broken, update_sensor_mode
from app.models import Sensor, SensorStatus
from app.schemas import (
    SensorBrokenUpdate,
    SensorCreate,
    SensorListOut,
    SensorModeUpdate,
    SensorOut,
    format_utc,
)
from app.services.health_checker import compute_sensor_status

logger = logging.getLogger(__name__)

router = APIRouter()


def _sensor_to_out(sensor: Sensor) -> SensorOut:
    status = compute_sensor_status(sensor)
    return SensorOut(
        serial_number=sensor.serial_number,
        mode=sensor.mode,
        status=status,
        broken=sensor.broken,
        last_received_at=(
            format_utc(sensor.last_received_at)
            if sensor.last_received_at
            else None
        ),
        latitude=sensor.latitude,
        longitude=sensor.longitude,
        created_at=format_utc(sensor.created_at),
        updated_at=format_utc(sensor.updated_at),
    )


@router.post("/sensors", response_model=SensorOut, status_code=201)
async def register_sensor(
    body: SensorCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await get_sensor(db, body.serial_number)
    if existing is not None:
        raise SensorAlreadyExistsError(body.serial_number)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    sensor = Sensor(
        serial_number=body.serial_number,
        mode=body.mode.value,
        status=SensorStatus.HEALTHY.value,
        broken=False,
        last_received_at=None,
        latitude=body.latitude,
        longitude=body.longitude,
        created_at=now,
        updated_at=now,
    )
    await create_sensor(db, sensor)
    await db.commit()
    return _sensor_to_out(sensor)


@router.get("/sensors", response_model=SensorListOut)
async def list_sensors(db: AsyncSession = Depends(get_db)):
    sensors = await get_all_sensors(db)
    return SensorListOut(data=[_sensor_to_out(s) for s in sensors])


@router.get("/sensors/{serial_number}", response_model=SensorOut)
async def get_sensor_detail(
    serial_number: str, db: AsyncSession = Depends(get_db)
):
    sensor = await get_sensor(db, serial_number)
    if sensor is None:
        raise SensorNotFoundError(serial_number)
    return _sensor_to_out(sensor)


@router.patch("/sensors/{serial_number}/mode", response_model=SensorOut)
async def change_sensor_mode(
    serial_number: str,
    body: SensorModeUpdate,
    db: AsyncSession = Depends(get_db),
):
    sensor = await update_sensor_mode(db, serial_number, body.mode.value)
    if sensor is None:
        raise SensorNotFoundError(serial_number)
    await db.commit()

    # 센서 시뮬레이터 동기화 (실패해도 무시)
    if settings.SENSOR_SIMULATOR_URL:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.patch(
                    f"{settings.SENSOR_SIMULATOR_URL}/sensors/{serial_number}/mode",
                    json={"mode": body.mode.value},
                )
        except Exception as e:
            logger.warning("센서 시뮬레이터 동기화 실패: %s", e)

    return _sensor_to_out(sensor)


@router.patch("/sensors/{serial_number}/broken", response_model=SensorOut)
async def set_sensor_broken(
    serial_number: str,
    body: SensorBrokenUpdate,
    db: AsyncSession = Depends(get_db),
):
    """센서 고장 시뮬레이션 (DB 저장 + 센서 시뮬레이터 동기화)"""
    sensor = await update_sensor_broken(db, serial_number, body.broken)
    if sensor is None:
        raise SensorNotFoundError(serial_number)
    await db.commit()

    # 센서 시뮬레이터 동기화 (실패해도 무시)
    if settings.SENSOR_SIMULATOR_URL:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.patch(
                    f"{settings.SENSOR_SIMULATOR_URL}/sensors/{serial_number}/broken",
                    json={"broken": body.broken},
                )
        except Exception as e:
            logger.warning("센서 시뮬레이터 고장 동기화 실패: %s", e)

    return _sensor_to_out(sensor)
