"""Pydantic schemas for Article endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.article import ArticleStatus
from app.schemas.category import CategoryResponse


class ArticleCreate(BaseModel):
    """Schema for creating a new article."""

    title: str
    body: str
    author: str
    status: ArticleStatus = ArticleStatus.draft
    category_ids: list[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article."""

    title: Optional[str] = None
    body: Optional[str] = None
    author: Optional[str] = None
    status: Optional[ArticleStatus] = None
    category_ids: list[int] = []


class ArticleResponse(BaseModel):
    """Schema for returning article data to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    author: str
    status: ArticleStatus
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryResponse] = []


class ArticleList(BaseModel):
    """Schema for returning a paginated list of articles."""

    model_config = ConfigDict(from_attributes=True)

    total: int
    items: list[ArticleResponse]
