"""Pydantic schemas for Article request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.article import ArticleStatus


class ArticleCreate(BaseModel):
    """Schema for creating a new article."""

    title: str = Field(..., max_length=200)
    body: str
    author: str = Field(..., max_length=100)
    status: ArticleStatus = ArticleStatus.draft


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article (all fields optional)."""

    title: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = None
    author: Optional[str] = Field(None, max_length=100)
    status: Optional[ArticleStatus] = None


class ArticleResponse(BaseModel):
    """Schema for article responses including all model fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    author: str
    status: ArticleStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ArticleList(BaseModel):
    """Schema for paginated list of articles."""

    items: list[ArticleResponse]
    total: int
