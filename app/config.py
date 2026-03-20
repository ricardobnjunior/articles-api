"""Application configuration."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    database_url: str = "sqlite:///./app.db"
    secret_key: str = "default-secret-key"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Return application settings."""
    return Settings()
