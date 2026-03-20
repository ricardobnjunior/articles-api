"""Category ORM model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    """ORM model for article categories.

    Attributes:
        id: Primary key.
        name: Display name of the category.
        slug: URL-friendly identifier.
        articles: Many-to-many relationship with Article.
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    articles = relationship(
        "Article",
        secondary="article_categories",
        back_populates="categories",
    )
