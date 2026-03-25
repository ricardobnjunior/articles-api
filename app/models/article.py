"""Article model definition."""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE")),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE")),
)


class ArticleStatus(str, enum.Enum):
    """Enumeration for article publication status."""

    draft = "draft"
    published = "published"
    archived = "archived"


class Article(Base):
    """ORM model representing a news/blog article."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.draft, nullable=False)
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
