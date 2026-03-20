"""Pydantic schemas for category request and response models."""

from typing import Optional

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    """Schema for creating a new category.

    Attributes:
        name: Category name (must be unique).
        description: Optional category description.
    """

    name: str
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category.

    Attributes:
        name: New category name.
        description: New category description.
    """

    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    """Schema for category data returned by the API.

    Attributes:
        id: Category primary key.
        name: Category name.
        description: Optional category description.
    """

    id: int
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}
