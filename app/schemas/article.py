"""Pydantic schemas for Article resources."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.category import CategoryResponse


class ArticleBase(BaseModel):
    """Base schema with common article fields.

    Attributes:
        title: Article title.
        body: Full article body text.
        author: Name of the article author.
        status: Publication status string.
    """

    title: str
    body: str
    author: str
    status: str = "draft"


class ArticleCreate(ArticleBase):
    """Schema for creating a new article.

    Attributes:
        category_ids: List of category IDs to associate with the article.
    """

    category_ids: List[int] = []


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article.

    Attributes:
        title: Optional new title.
        body: Optional new body.
        author: Optional new author.
        status: Optional new status.
        category_ids: List of category IDs to assign (replaces existing).
    """

    title: Optional[str] = None
    body: Optional[str] = None
    author: Optional[str] = None
    status: Optional[str] = None
    category_ids: List[int] = []


class ArticleResponse(ArticleBase):
    """Schema for article API responses.

    Attributes:
        id: Article primary key.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        categories: List of associated categories.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    categories: List[CategoryResponse] = []


class ArticleList(BaseModel):
    """Schema for paginated article list responses.

    Attributes:
        items: List of articles.
        total: Total number of articles.
    """

    items: List[ArticleResponse]
    total: int
