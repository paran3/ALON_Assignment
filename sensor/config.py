from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_URL: str = "http://127.0.0.1:8000"
    SENSOR_PORT: int = 8001
    NORMAL_INTERVAL: int = 600
    EMERGENCY_INTERVAL: int = 10

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
