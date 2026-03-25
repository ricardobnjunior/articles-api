"""Pydantic schemas for Article endpoints."""

import math
from datetime import datetime

from pydantic import BaseModel

from app.models.article import ArticleStatus


class CategoryBase(BaseModel):
    """Base schema for category."""

    id: int
    name: str

    model_config = {"from_attributes": True}


class ArticleCreate(BaseModel):
    """Schema for creating an article."""

    title: str
    body: str
    author: str
    status: ArticleStatus = ArticleStatus.draft
    category_ids: list[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an article."""

    title: str | None = None
    body: str | None = None
    author: str | None = None
    status: ArticleStatus | None = None
    category_ids: list[int] | None = None


class ArticleResponse(BaseModel):
    """Schema for article response."""

    id: int
    title: str
    body: str
    author: str
    status: ArticleStatus
    categories: list[CategoryBase] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    total: int
    page: int
    per_page: int
    pages: int


class ArticleList(BaseModel):
    """Schema for paginated list of articles."""

    items: list[ArticleResponse]
    meta: PaginationMeta
