"""Central API router for version 1."""

from fastapi import APIRouter


router = APIRouter(prefix="/api/v1")

router.include_router(articles.router, prefix="/articles", tags=["articles"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
