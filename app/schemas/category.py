"""Pydantic schemas for Category endpoints."""

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    """Schema for creating a category."""

    name: str


class CategoryResponse(BaseModel):
    """Schema for category response."""

    id: int
    name: str

    model_config = {"from_attributes": True}
