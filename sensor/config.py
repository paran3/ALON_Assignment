from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_URL: str = ""
    SENSOR_PORT: int = 9001
    NORMAL_INTERVAL: int = 600
    EMERGENCY_INTERVAL: int = 10
    BULK_COUNT: int = 10  # 벌크 전송 시 모아서 보낼 데이터 건수

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
