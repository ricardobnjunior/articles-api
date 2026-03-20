"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings
from app.database import create_tables

app = FastAPI(title="Content API")

create_tables()

app.include_router(api_router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Return service health status.

    Returns:
        dict: A mapping with 'status' and 'environment' keys.
    """
    return {"status": "ok", "environment": settings.environment}
