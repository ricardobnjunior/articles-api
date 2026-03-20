"""Pydantic schemas for article request and response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.article import ArticleStatus


class CategoryBrief(BaseModel):
    """Brief category representation used inside article responses.

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
        status: Publication status (defaults to DRAFT).
        category_ids: Optional list of category IDs to associate.
    """

    title: str
    content: str
    status: ArticleStatus = ArticleStatus.DRAFT
    category_ids: list[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article.

    All fields are optional; only provided fields will be updated.

    Attributes:
        title: New article title.
        content: New article body content.
        status: New publication status.
        category_ids: New list of category IDs.
        image_url: New image URL (or None to clear).
    """

    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ArticleStatus] = None
    category_ids: Optional[list[int]] = None
    image_url: Optional[str] = None


class ArticleResponse(BaseModel):
    """Schema for article data returned by the API.

    Attributes:
        id: Article primary key.
        title: Article title.
        content: Article body content.
        status: Publication status.
        image_url: Optional URL path to the article image.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        categories: List of associated categories.
    """

    id: int
    title: str
    content: str
    status: ArticleStatus
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryBrief] = []

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses.

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
    """Schema for paginated article list response.

    Attributes:
        items: List of articles on the current page.
        meta: Pagination metadata.
    """

    items: list[ArticleResponse]
    meta: PaginationMeta
