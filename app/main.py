"""
FastAPI application entry point.
"""
from fastapi import FastAPI

from app.api.router import api_router
from app.config import get_settings
from app.database import create_tables

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Content API",
    description="Backend API for content management",
    version="1.0.0",
)

# Include central API router
app.include_router(api_router)


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint.

    Returns:
        dict: Status and environment information.
    """
    return {"status": "ok", "environment": settings.environment}


@app.on_event("startup")
def on_startup():
    """Application startup event handler.

    Creates database tables if they don't exist.
    """
    create_tables()
