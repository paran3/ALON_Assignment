from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "IoT Monitoring API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./iot_monitoring.db"

    # 센서 상태 검증 간격 (초)
    HEALTH_CHECK_INTERVAL_SECONDS: int = 5

    # 센서 모드별 전송 주기 (초)
    NORMAL_INTERVAL_SECONDS: int = 600
    EMERGENCY_INTERVAL_SECONDS: int = 10

    # 상태 판별 허용 오차 (초)
    HEALTH_TOLERANCE_SECONDS: int = 30

    # 가상 센서 시뮬레이터 URL (빈 문자열이면 동기화 비활성)
    SENSOR_SIMULATOR_URL: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
