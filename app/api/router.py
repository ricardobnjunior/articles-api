"""Central API router with versioned prefix."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Future endpoint routers will be included here via:
# api_router.include_router(some_router, prefix="/resource", tags=["resource"])
