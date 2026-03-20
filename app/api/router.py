"""Main API router that aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints.articles import router as articles_router
from app.api.endpoints.categories import router as categories_router
from app.api.endpoints.export import router as export_router
from app.api.endpoints.stats import router as stats_router

router = APIRouter()

router.include_router(articles_router, prefix="/articles", tags=["articles"])
router.include_router(categories_router, prefix="/categories", tags=["categories"])
router.include_router(stats_router, prefix="/stats", tags=["stats"])
router.include_router(export_router, prefix="/export", tags=["export"])
