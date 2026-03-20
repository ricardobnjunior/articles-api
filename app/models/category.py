"""SQLAlchemy ORM model for categories."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.article import article_categories


class Category(Base):
    """ORM model representing an article category.

    Attributes:
        id: Primary key.
        name: Unique category name.
        description: Optional category description.
        articles: Many-to-many relationship to Article.
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    articles = relationship(
        "Article",
        secondary=article_categories,
        back_populates="categories",
    )
