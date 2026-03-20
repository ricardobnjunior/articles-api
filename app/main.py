"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router
from app.database import create_tables


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application.

    Returns:
        A configured FastAPI instance.
    """
    application = FastAPI(
        title="Articles API",
        description="REST API for managing articles.",
        version="1.0.0",
    )

    application.include_router(api_router)

    @application.get("/health", tags=["health"])
    def health_check() -> dict:
        """Return a simple health status.

        Returns:
            A dict with status key.
        """
        return {"status": "ok"}

    create_tables()

    return application


app = create_app()
