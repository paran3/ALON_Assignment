import logging
from datetime import datetime, timezone

from dateutil import parser as dateutil_parser

from app.core.db import async_session
from app.core.exceptions import DataProcessingError, UnregisteredSensorError
from app.crud import (
    create_sensor_data,
    get_sensor,
    update_sensor_on_data,
    update_task_status,
)
from app.models import SensorData, TaskStatus
from app.schemas import SensorDataIn

logger = logging.getLogger(__name__)


def parse_timestamp_to_utc(timestamp_str: str) -> datetime:
    dt = dateutil_parser.isoparse(timestamp_str)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


async def process_sensor_data(task_id: str, items: list[SensorDataIn]) -> None:
    async with async_session() as db:
        try:
            await update_task_status(
                db, task_id, status=TaskStatus.PROCESSING.value
            )
            now = datetime.utcnow()
            processed = 0
            errors: list[str] = []

            for item in items:
                try:
                    sensor = await get_sensor(db, item.serial_number)
                    if sensor is None:
                        raise UnregisteredSensorError(item.serial_number)

                    utc_timestamp = parse_timestamp_to_utc(item.timestamp)

                    sensor_data = SensorData(
                        serial_number=item.serial_number,
                        timestamp=utc_timestamp,
                        created_at=now,
                        mode=item.mode.value,
                        temperature=item.temperature,
                        humidity=item.humidity,
                        pressure=item.pressure,
                        latitude=item.location.lat,
                        longitude=item.location.lng,
                        air_quality=item.air_quality,
                        task_id=task_id,
                    )
                    await create_sensor_data(db, sensor_data)

                    await update_sensor_on_data(
                        db,
                        serial_number=item.serial_number,
                        mode=item.mode.value,
                        latitude=item.location.lat,
                        longitude=item.location.lng,
                        received_at=now,
                    )
                    processed += 1
                except UnregisteredSensorError as e:
                    errors.append(str(e))
                    continue
                except Exception as e:
                    err = DataProcessingError(item.serial_number, str(e))
                    logger.error(str(err))
                    errors.append(str(err))

            await db.commit()

            error_msg = "; ".join(errors) if errors else None
            await update_task_status(
                db,
                task_id,
                status=TaskStatus.COMPLETED.value,
                processed_count=processed,
                error_message=error_msg,
                completed_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.exception("Task %s failed", task_id)
            await update_task_status(
                db,
                task_id,
                status=TaskStatus.FAILED.value,
                error_message=str(e),
                completed_at=datetime.utcnow(),
            )
