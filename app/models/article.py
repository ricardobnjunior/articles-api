"""Article ORM model and association table for article-category many-to-many."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base

article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE")),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE")),
)


class ArticleStatus(str, enum.Enum):
    """Enumeration of possible article publication statuses."""

    draft = "draft"
    published = "published"
    archived = "archived"


class Article(Base):
    """ORM model representing a content article.

    Attributes:
        id: Primary key.
        title: Article title.
        body: Full article body text.
        author: Name of the article author.
        status: Publication status (draft, published, archived).
        created_at: Timestamp when the article was created.
        updated_at: Timestamp when the article was last updated.
        categories: Many-to-many relationship with Category.
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    status = Column(Enum(ArticleStatus), nullable=False, default=ArticleStatus.draft)
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
