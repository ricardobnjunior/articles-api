"""Pydantic schemas for Category endpoints."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class CategoryCreate(BaseModel):
    """Schema for creating a new category."""

    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_max_length(cls, v: str) -> str:
        """Validate that name does not exceed 100 characters."""
        if len(v) > 100:
            raise ValueError("name must be at most 100 characters")
        return v


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_max_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate that name does not exceed 100 characters."""
        if v is not None and len(v) > 100:
            raise ValueError("name must be at most 100 characters")
        return v


class CategoryResponse(BaseModel):
    """Schema for category responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
