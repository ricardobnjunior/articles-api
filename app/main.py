"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events.

    Args:
        app: The FastAPI application instance.
    """
    create_tables()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A fully configured FastAPI application instance.
    """
    settings = get_settings()

    application = FastAPI(title="Content API", lifespan=lifespan)

    application.include_router(api_router)

    @application.get("/health")
    def health_check():
        """Return application health status.

        Returns:
            dict: A dictionary with status and current environment.
        """
        return {"status": "ok", "environment": settings.environment}

    return application


app = create_app()
