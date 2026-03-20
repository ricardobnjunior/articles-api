"""Article ORM model."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base

article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class ArticleStatus(str, enum.Enum):
    """Enumeration of possible article statuses."""

    draft = "draft"
    published = "published"
    archived = "archived"


class Article(Base):
    """ORM model for articles.

    Attributes:
        id: Primary key.
        title: Article title.
        body: Article body content.
        author: Author name.
        status: Publication status.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        categories: Many-to-many relationship with Category.
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False, index=True)
    status = Column(
        Enum(ArticleStatus),
        nullable=False,
        default=ArticleStatus.draft,
        index=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    categories = relationship(
        "Category",
        secondary=article_categories,
        back_populates="articles",
    )
