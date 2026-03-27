"""CRUD operations for Article resources."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus
from app.models.category import Category
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article, optionally associating it with categories.

    Args:
        db: SQLAlchemy database session.
        data: Article creation data including optional category_ids.

    Returns:
        The newly created Article instance.
    """
    article = Article(
        title=data.title,
        body=data.body,
        author=data.author,
        status=ArticleStatus(data.status),
    )
    db.add(article)
    db.flush()

    if data.category_ids:
        categories = (
            db.query(Category)
            .filter(Category.id.in_(data.category_ids))
            .all()
        )
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """Retrieve a single article by its primary key.

    Args:
        db: SQLAlchemy database session.
        article_id: The article's primary key.

    Returns:
        The Article instance if found, otherwise None.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(db: Session, skip: int = 0, limit: int = 20) -> List[Article]:
    """Retrieve a paginated list of articles.

    Args:
        db: SQLAlchemy database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        A list of Article instances.
    """
    return db.query(Article).offset(skip).limit(limit).all()


def update_article(
    db: Session, article_id: int, data: ArticleUpdate
) -> Optional[Article]:
    """Update an existing article.

    Args:
        db: SQLAlchemy database session.
        article_id: The article's primary key.
        data: Fields to update; category_ids replaces the current categories.

    Returns:
        The updated Article instance, or None if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    category_ids = update_data.pop("category_ids", None)

    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = ArticleStatus(update_data["status"])

    for field, value in update_data.items():
        setattr(article, field, value)

    if category_ids is not None:
        categories = (
            db.query(Category)
            .filter(Category.id.in_(category_ids))
            .all()
        ) if category_ids else []
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by its primary key.

    Args:
        db: SQLAlchemy database session.
        article_id: The article's primary key.

    Returns:
        True if the article was deleted, False if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return False
    db.delete(article)
    db.commit()
    return True
