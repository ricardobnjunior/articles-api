"""Application configuration using pydantic-settings."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: SQLAlchemy database connection URL.
        secret_key: Secret key for JWT signing.
        environment: Deployment environment name.
        upload_dir: Directory for storing uploaded files.
    """

    database_url: str = "sqlite:///./articles.db"
    secret_key: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    environment: str = "development"
    upload_dir: str = "uploads"

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Returns:
        The singleton Settings instance.
    """
    return Settings()
