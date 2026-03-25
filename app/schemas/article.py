"""Pydantic schemas for article request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    """Schema for category API responses embedded in articles.

    Attributes:
        id: Category primary key.
        name: Category name.
    """

    id: int
    name: str

    model_config = {"from_attributes": True}


class ArticleCreate(BaseModel):
    """Schema for creating a new article.

    Attributes:
        title: Article title.
        content: Article body content.
        status: Publication status (defaults to draft).
        category_ids: List of category IDs to associate.
    """

    title: str
    content: str
    status: str = "draft"
    category_ids: List[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article.

    Attributes:
        title: Optional new title.
        content: Optional new content.
        status: Optional new status.
        category_ids: Optional new list of category IDs.
        image_url: Optional new image URL.
    """

    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    category_ids: Optional[List[int]] = None
    image_url: Optional[str] = None


class ArticleResponse(BaseModel):
    """Schema for article API responses.

    Attributes:
        id: Article primary key.
        title: Article title.
        content: Article body content.
        status: Publication status string.
        image_url: Optional URL path to the article image.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        categories: List of associated categories.
    """

    id: int
    title: str
    content: str
    status: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    categories: List[CategoryResponse] = []

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Metadata for paginated responses.

    Attributes:
        total: Total number of items.
        page: Current page number.
        per_page: Items per page.
        pages: Total number of pages.
    """

    total: int
    page: int
    per_page: int
    pages: int


class ArticleList(BaseModel):
    """Schema for paginated list of articles.

    Attributes:
        items: List of article responses.
        meta: Pagination metadata.
    """

    items: List[ArticleResponse]
    meta: PaginationMeta
