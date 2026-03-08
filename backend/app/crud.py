from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BackgroundTask, Sensor, SensorData, SensorStatus, TaskStatus


# --- SensorData ---


async def create_sensor_data(db: AsyncSession, data: SensorData) -> SensorData:
    db.add(data)
    await db.flush()
    return data


async def get_sensor_data(
    db: AsyncSession,
    *,
    serial_number: str | None = None,
    mode: str | None = None,
    timestamp_from: datetime | None = None,
    timestamp_to: datetime | None = None,
    created_at_from: datetime | None = None,
    created_at_to: datetime | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[SensorData], int]:
    query = select(SensorData)
    count_query = select(func.count()).select_from(SensorData)

    filters = []
    if serial_number:
        filters.append(SensorData.serial_number == serial_number)
    if mode:
        filters.append(SensorData.mode == mode)
    if timestamp_from:
        filters.append(SensorData.timestamp >= timestamp_from)
    if timestamp_to:
        filters.append(SensorData.timestamp <= timestamp_to)
    if created_at_from:
        filters.append(SensorData.created_at >= created_at_from)
    if created_at_to:
        filters.append(SensorData.created_at <= created_at_to)

    for f in filters:
        query = query.where(f)
        count_query = count_query.where(f)

    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(SensorData.id.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


# --- Sensor ---


async def create_sensor(db: AsyncSession, sensor: Sensor) -> Sensor:
    db.add(sensor)
    await db.flush()
    return sensor


async def get_sensor(db: AsyncSession, serial_number: str) -> Sensor | None:
    result = await db.execute(
        select(Sensor).where(Sensor.serial_number == serial_number)
    )
    return result.scalar_one_or_none()


async def get_all_sensors(db: AsyncSession) -> list[Sensor]:
    result = await db.execute(select(Sensor).order_by(Sensor.serial_number))
    return list(result.scalars().all())


async def update_sensor_mode(
    db: AsyncSession, serial_number: str, mode: str
) -> Sensor | None:
    sensor = await get_sensor(db, serial_number)
    if sensor is None:
        return None
    sensor.mode = mode
    sensor.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.flush()
    return sensor


async def update_sensor_on_data(
    db: AsyncSession,
    *,
    serial_number: str,
    mode: str,
    latitude: float,
    longitude: float,
    received_at: datetime,
) -> Sensor | None:
    sensor = await get_sensor(db, serial_number)
    if sensor is None:
        return None
    sensor.mode = mode
    sensor.last_received_at = received_at
    sensor.latitude = latitude
    sensor.longitude = longitude
    sensor.status = SensorStatus.HEALTHY.value
    sensor.updated_at = received_at
    await db.flush()
    return sensor


# --- BackgroundTask ---


async def create_background_task(
    db: AsyncSession, task_id: str, total_count: int
) -> BackgroundTask:
    task = BackgroundTask(
        id=task_id,
        status=TaskStatus.PENDING.value,
        total_count=total_count,
        processed_count=0,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(task)
    await db.commit()
    return task


async def get_background_task(
    db: AsyncSession, task_id: str
) -> BackgroundTask | None:
    result = await db.execute(
        select(BackgroundTask).where(BackgroundTask.id == task_id)
    )
    return result.scalar_one_or_none()


async def update_task_status(
    db: AsyncSession,
    task_id: str,
    *,
    status: str | None = None,
    processed_count: int | None = None,
    error_message: str | None = None,
    completed_at: datetime | None = None,
) -> None:
    result = await db.execute(
        select(BackgroundTask).where(BackgroundTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task is None:
        return
    if status is not None:
        task.status = status
    if processed_count is not None:
        task.processed_count = processed_count
    if error_message is not None:
        task.error_message = error_message
    if completed_at is not None:
        task.completed_at = completed_at
    await db.commit()
