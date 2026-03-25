"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "News API"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Return application settings."""
    return Settings()
