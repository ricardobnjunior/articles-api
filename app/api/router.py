"""Central API router with /api/v1 prefix."""

from fastapi import APIRouter

from app.api.endpoints.articles import router as articles_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(articles_router)
