from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = Field(default="development")
    DATABASE_URL: str = Field(default="postgresql+psycopg://avip:avip@localhost:5432/avip")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    LOG_LEVEL: str = Field(default="INFO")
    MODEL_PATH: str = Field(default="/models")
    VIDEO_SOURCE: str = Field(default="rtsp://example-stream:8554/stream")
    AUTH_SECRET_KEY: str = Field(
        default="avip-development-secret-change-in-production",
        min_length=32,
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0, le=1440)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
