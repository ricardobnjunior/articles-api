"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        database_url: SQLAlchemy database connection URL.
        secret_key: Secret key for JWT token signing.
        environment: Deployment environment name.
        upload_dir: Directory path for storing uploaded files.
    """

    database_url: str = "sqlite:///./articles.db"
    secret_key: str = "dev-secret-key-change-in-production"
    environment: str = "development"
    upload_dir: str = "uploads"

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance.

    Returns:
        Singleton Settings instance.
    """
    return Settings()


settings = get_settings()
