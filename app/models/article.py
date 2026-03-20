"""Article model for the blog application."""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import relationship

from app.database import Base

# Association table for Article <-> Category many-to-many relationship
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE")),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE")),
)


class ArticleStatus(str, enum.Enum):
    """Status enumeration for articles."""

    draft = "draft"
    published = "published"
    archived = "archived"


class Article(Base):
    """SQLAlchemy model representing a blog article."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.draft, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Many-to-many relationship with Category
    categories = relationship("Category", secondary=article_categories, back_populates="articles")
