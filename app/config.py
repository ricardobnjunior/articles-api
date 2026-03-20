"""Application configuration via Pydantic Settings."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: SQLAlchemy connection string.
        secret_key: Secret key for signing tokens.
        environment: Deployment environment name.
    """

    database_url: str = "sqlite:///:memory:"
    secret_key: str = "default-secret-key"
    environment: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Returns:
        A singleton Settings instance.
    """
    return Settings()
