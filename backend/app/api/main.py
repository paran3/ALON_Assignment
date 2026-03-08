from fastapi import APIRouter

from app.api.routes import sensor_data, sensors, tasks

api_router = APIRouter()
api_router.include_router(sensor_data.router, tags=["sensor-data"])
api_router.include_router(sensors.router, tags=["sensors"])
api_router.include_router(tasks.router, tags=["tasks"])
