from datetime import datetime

from pydantic import BaseModel, Field

from app.models import SensorMode, SensorStatus, TaskStatus


# --- Utility ---


def format_utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# --- Request schemas ---


class LocationIn(BaseModel):
    lat: float
    lng: float


class SensorDataIn(BaseModel):
    serial_number: str
    timestamp: str
    mode: SensorMode
    temperature: float
    humidity: float
    pressure: float
    location: LocationIn
    air_quality: int


class SensorCreate(BaseModel):
    serial_number: str
    latitude: float
    longitude: float
    mode: SensorMode = SensorMode.NORMAL


class SensorModeUpdate(BaseModel):
    mode: SensorMode


class SensorBrokenUpdate(BaseModel):
    broken: bool


# --- Response schemas ---


class TaskAccepted(BaseModel):
    task_id: str
    message: str = "Data accepted for processing"


class LocationOut(BaseModel):
    lat: float
    lng: float


class MetricsOut(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    air_quality: int


class SensorDataOut(BaseModel):
    id: int
    serial_number: str
    timestamp: str
    server_received_at: str
    mode: SensorMode
    metrics: MetricsOut
    location: LocationOut


class PaginationOut(BaseModel):
    total_count: int
    current_page: int
    limit: int
    total_pages: int
    has_next_page: bool
    has_prev_page: bool


class SensorDataListOut(BaseModel):
    success: bool = True
    data: list[SensorDataOut]
    pagination: PaginationOut


class SensorOut(BaseModel):
    serial_number: str
    mode: SensorMode
    status: SensorStatus
    broken: bool
    last_received_at: str | None
    latitude: float
    longitude: float
    created_at: str
    updated_at: str


class SensorListOut(BaseModel):
    success: bool = True
    data: list[SensorOut]


class TaskStatusOut(BaseModel):
    id: str
    status: TaskStatus
    total_count: int
    processed_count: int
    error_message: str | None
    created_at: str
    completed_at: str | None
