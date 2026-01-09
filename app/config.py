"""Application configuration settings."""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Excel2Markdown"
    app_version: str = "1.0.0"
    debug: bool = False

    # File handling
    max_file_size_mb: int = 10
    allowed_extensions: List[str] = [".xls", ".xlsx"]

    # Storage paths
    storage_dir: Path = Path("storage")
    uploads_dir: Path = Path("storage/uploads")
    results_dir: Path = Path("storage/results")

    # Cleanup settings
    file_retention_days: int = 7

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    @property
    def max_file_size_bytes(self) -> int:
        """Return max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
