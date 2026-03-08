import logging
from datetime import datetime

from sqlalchemy import select

from app.core.config import settings
from app.core.db import async_session
from app.models import Sensor, SensorMode, SensorStatus

logger = logging.getLogger(__name__)


def compute_sensor_status(sensor: Sensor, now: datetime | None = None) -> str:
    if sensor.last_received_at is None:
        return SensorStatus.MISSING.value

    if now is None:
        now = datetime.utcnow()

    if sensor.mode == SensorMode.EMERGENCY.value:
        expected = settings.EMERGENCY_INTERVAL_SECONDS
    else:
        expected = settings.NORMAL_INTERVAL_SECONDS

    threshold = expected + settings.HEALTH_TOLERANCE_SECONDS
    elapsed = (now - sensor.last_received_at).total_seconds()
    return (
        SensorStatus.MISSING.value
        if elapsed > threshold
        else SensorStatus.HEALTHY.value
    )


async def check_all_sensors() -> None:
    async with async_session() as db:
        result = await db.execute(select(Sensor))
        sensors = result.scalars().all()
        now = datetime.utcnow()
        for sensor in sensors:
            new_status = compute_sensor_status(sensor, now)
            if sensor.status != new_status:
                logger.info(
                    "Sensor %s status: %s -> %s",
                    sensor.serial_number,
                    sensor.status,
                    new_status,
                )
                sensor.status = new_status
        await db.commit()
