"""SQLAlchemy ORM model for articles."""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# Association table for many-to-many relationship between articles and categories
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class ArticleStatus(str, enum.Enum):
    """Enumeration of possible article statuses."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Article(Base):
    """ORM model representing an article.

    Attributes:
        id: Primary key.
        title: Article title.
        content: Article body content.
        status: Publication status.
        image_url: Optional URL path to the article's image.
        created_at: Timestamp when the article was created.
        updated_at: Timestamp when the article was last updated.
        categories: Many-to-many relationship to Category.
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    status = Column(
        Enum(ArticleStatus),
        default=ArticleStatus.DRAFT,
        nullable=False,
    )
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    categories = relationship(
        "Category",
        secondary=article_categories,
        back_populates="articles",
    )
