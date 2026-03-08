import asyncio
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud import create_background_task, get_sensor_data
from app.models import SensorMode
from app.schemas import (
    LocationOut,
    MetricsOut,
    PaginationOut,
    SensorDataIn,
    SensorDataListOut,
    SensorDataOut,
    TaskAccepted,
    format_utc,
)
from app.services.data_ingestion import process_sensor_data

router = APIRouter()


@router.post("/sensor-data", response_model=TaskAccepted, status_code=202)
async def receive_sensor_data(
    payload: SensorDataIn | list[SensorDataIn],
    db: AsyncSession = Depends(get_db),
):
    items = payload if isinstance(payload, list) else [payload]
    task_id = str(uuid.uuid4())

    await create_background_task(db, task_id, total_count=len(items))
    asyncio.create_task(process_sensor_data(task_id, items))

    return TaskAccepted(task_id=task_id)


@router.get("/sensor-data", response_model=SensorDataListOut)
async def list_sensor_data(
    serial_number: str | None = Query(None),
    mode: SensorMode | None = Query(None),
    timestamp_from: datetime | None = Query(None),
    timestamp_to: datetime | None = Query(None),
    created_at_from: datetime | None = Query(None),
    created_at_to: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    mode_value = mode.value if mode else None
    data_list, total = await get_sensor_data(
        db,
        serial_number=serial_number,
        mode=mode_value,
        timestamp_from=timestamp_from,
        timestamp_to=timestamp_to,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        page=page,
        limit=limit,
    )

    total_pages = max(1, (total + limit - 1) // limit)

    items = [
        SensorDataOut(
            id=d.id,
            serial_number=d.serial_number,
            timestamp=format_utc(d.timestamp),
            server_received_at=format_utc(d.created_at),
            mode=d.mode,
            metrics=MetricsOut(
                temperature=d.temperature,
                humidity=d.humidity,
                pressure=d.pressure,
                air_quality=d.air_quality,
            ),
            location=LocationOut(lat=d.latitude, lng=d.longitude),
        )
        for d in data_list
    ]

    return SensorDataListOut(
        data=items,
        pagination=PaginationOut(
            total_count=total,
            current_page=page,
            limit=limit,
            total_pages=total_pages,
            has_next_page=page < total_pages,
            has_prev_page=page > 1,
        ),
    )
