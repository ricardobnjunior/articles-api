"""SQLAlchemy ORM model for categories."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.article import article_categories


class Category(Base):
    """ORM model representing a category.

    Attributes:
        id: Primary key.
        name: Category name (unique).
        articles: Many-to-many relationship with Article model.
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)

    articles = relationship(
        "Article",
        secondary=article_categories,
        back_populates="categories",
    )
