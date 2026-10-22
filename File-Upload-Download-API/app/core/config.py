
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./file_management_dev.db",
        validation_alias="DATABASE_URL",
    )

    jwt_secret_key: str = Field(
        default="development-only-change-this-secret",
        validation_alias="JWT_SECRET_KEY",
    )

    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias="JWT_ALGORITHM",
    )

    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    upload_dir: str = Field(
        default="uploads",
        validation_alias="UPLOAD_DIR",
    )

    max_file_size: int = Field(
        default=5 * 1024 * 1024,
        validation_alias="MAX_FILE_SIZE",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()