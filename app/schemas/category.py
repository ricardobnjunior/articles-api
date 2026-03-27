"""Pydantic schemas for Category resources."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """Schema for creating a new category.

    Attributes:
        name: Category name (max 100 characters).
        description: Optional category description.
    """

    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category.

    Attributes:
        name: Optional new category name (max 100 characters).
        description: Optional new description.
    """

    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    """Schema for category API responses.

    Attributes:
        id: Category primary key.
        name: Category name.
        slug: URL-safe slug auto-generated from name.
        description: Optional category description.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
