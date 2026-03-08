from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.exceptions import TaskNotFoundError
from app.crud import get_background_task
from app.schemas import TaskStatusOut, format_utc

router = APIRouter()


@router.get("/tasks/{task_id}", response_model=TaskStatusOut)
async def get_task_status(
    task_id: str, db: AsyncSession = Depends(get_db)
):
    task = await get_background_task(db, task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    return TaskStatusOut(
        id=task.id,
        status=task.status,
        total_count=task.total_count,
        processed_count=task.processed_count,
        error_message=task.error_message,
        created_at=format_utc(task.created_at),
        completed_at=(
            format_utc(task.completed_at) if task.completed_at else None
        ),
    )
