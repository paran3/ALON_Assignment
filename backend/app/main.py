from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine
from app.core.exceptions import (
    SensorAlreadyExistsError,
    SensorNotFoundError,
    TaskNotFoundError,
)
from app.models import Base
from app.services.health_checker import check_all_sensors

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler.add_job(
        check_all_sensors,
        "interval",
        seconds=settings.HEALTH_CHECK_INTERVAL_SECONDS,
        id="health_checker",
    )
    scheduler.start()

    yield

    scheduler.shutdown()
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(SensorNotFoundError)
async def sensor_not_found_handler(request: Request, exc: SensorNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(SensorAlreadyExistsError)
async def sensor_already_exists_handler(
    request: Request, exc: SensorAlreadyExistsError
):
    return JSONResponse(status_code=409, content={"detail": str(exc)})
