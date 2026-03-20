"""Central API router aggregating all versioned endpoint routers."""

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Future endpoint routers are included here, e.g.:
# from app.api.endpoints import some_router
# api_router.include_router(some_router, prefix="/some-resource", tags=["some-resource"])
