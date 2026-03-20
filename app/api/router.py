"""Central API router that includes all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints.articles import router as articles_router
from app.api.endpoints.categories import router as categories_router

router = APIRouter()
router.include_router(articles_router)
router.include_router(categories_router)
