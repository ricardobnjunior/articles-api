"""CRUD operations for articles."""

import math
from typing import Optional

from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus
from app.schemas.article import ArticleCreate, ArticleUpdate


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """Retrieve a single article by ID.

    Args:
        db: Database session.
        article_id: Primary key of the article.

    Returns:
        The Article instance, or None if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session,
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    status: Optional[ArticleStatus] = None,
    category_id: Optional[int] = None,
) -> tuple[list[Article], int]:
    """Retrieve a paginated list of articles with optional filters.

    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        search: Optional search string to filter by title or content.
        status: Optional status filter.
        category_id: Optional category ID to filter by.

    Returns:
        A tuple of (list of articles, total count).
    """
    query = db.query(Article)

    if search:
        query = query.filter(
            Article.title.ilike(f"%{search}%") | Article.content.ilike(f"%{search}%")
        )

    if status:
        query = query.filter(Article.status == status)

    if category_id:
        from app.models.article import article_categories
        query = query.join(
            article_categories,
            Article.id == article_categories.c.article_id,
        ).filter(article_categories.c.category_id == category_id)

    total = query.count()
    offset = (page - 1) * per_page
    articles = query.offset(offset).limit(per_page).all()

    return articles, total


def create_article(db: Session, article_in: ArticleCreate) -> Article:
    """Create a new article.

    Args:
        db: Database session.
        article_in: Schema with article creation data.

    Returns:
        The newly created Article instance.
    """
    from app.models.category import Category

    db_article = Article(
        title=article_in.title,
        content=article_in.content,
        status=article_in.status,
    )

    if article_in.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(article_in.category_ids)
        ).all()
        db_article.categories = categories

    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def update_article(
    db: Session, article: Article, article_in: ArticleUpdate
) -> Article:
    """Update an existing article.

    Args:
        db: Database session.
        article: The existing Article ORM instance.
        article_in: Schema with fields to update (unset fields are ignored).

    Returns:
        The updated Article instance.
    """
    from app.models.category import Category

    update_data = article_in.model_dump(exclude_unset=True)

    # Handle category_ids separately
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")
        if category_ids is not None:
            categories = db.query(Category).filter(
                Category.id.in_(category_ids)
            ).all()
            article.categories = categories
        else:
            article.categories = []

    # Apply remaining fields including image_url
    for field, value in update_data.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article: Article) -> None:
    """Delete an article from the database.

    Args:
        db: Database session.
        article: The Article instance to delete.
    """
    db.delete(article)
    db.commit()
