"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import router
from app.config import get_settings
from app.database import Base, engine


def create_tables() -> None:
    """Create all database tables defined in the ORM models."""
    Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    application = FastAPI(
        title="Articles API",
        description="REST API for managing articles with categories and image uploads",
        version="1.0.0",
    )

    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Mount static files for serving uploaded images
    application.mount(
        "/uploads",
        StaticFiles(directory=settings.upload_dir),
        name="uploads",
    )

    # Include API router
    application.include_router(router, prefix="/api/v1")

    @application.get("/health")
    def health_check() -> dict:
        """Health check endpoint.

        Returns:
            Dictionary with status and environment info.
        """
        return {"status": "ok", "environment": settings.environment}

    # Create tables on startup
    create_tables()

    return application


app = create_app()
