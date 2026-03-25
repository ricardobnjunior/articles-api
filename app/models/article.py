"""SQLAlchemy model for Article."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum
from app.database import Base
import enum


class ArticleStatus(str, enum.Enum):
    """Enumeration of possible article statuses."""

    draft = "draft"
    published = "published"


class Article(Base):
    """Article model representing a blog/article entry in the database."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    status = Column(SQLEnum(ArticleStatus), default=ArticleStatus.draft, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
