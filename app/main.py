"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    application = FastAPI(
        title="Articles API",
        description="REST API for managing articles with search and filtering",
        version="1.0.0",
    )

    application.include_router(api_router)

    return application


app = create_app()
