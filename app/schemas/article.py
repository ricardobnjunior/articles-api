"""Pydantic schemas for Article endpoints."""

import math
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.article import ArticleStatus


class CategoryResponse(BaseModel):
    """Schema for category in article response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class ArticleCreate(BaseModel):
    """Schema for creating an article."""

    title: str
    body: str
    author: str
    status: ArticleStatus = ArticleStatus.draft
    category_ids: list[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an article."""

    title: Optional[str] = None
    body: Optional[str] = None
    author: Optional[str] = None
    status: Optional[ArticleStatus] = None
    category_ids: Optional[list[int]] = None


class ArticleResponse(BaseModel):
    """Schema for article response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    author: str
    status: ArticleStatus
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryResponse] = []


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int
    page: int
    per_page: int
    pages: int


class ArticleList(BaseModel):
    """Schema for paginated list of articles."""

    items: list[ArticleResponse]
    meta: PaginationMeta
