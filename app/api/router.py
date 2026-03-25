"""
Central API router with prefix for all API endpoints.
"""
from fastapi import APIRouter

# Central router with API version prefix
# All future endpoint routers should be included here
api_router = APIRouter(prefix="/api/v1")
