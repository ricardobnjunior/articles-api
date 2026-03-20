"""CRUD operations for articles."""

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus, article_categories
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article.

    Args:
        db: Database session.
        data: Article creation data.

    Returns:
        The newly created Article instance.
    """
    from app.models.category import Category

    article = Article(
        title=data.title,
        body=data.body,
        author=data.author,
        status=data.status,
    )

    if data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        article.categories = categories

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """Retrieve an article by its ID.

    Args:
        db: Database session.
        article_id: Primary key of the article.

    Returns:
        The Article instance if found, else None.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    status: Optional[ArticleStatus] = None,
    author: Optional[str] = None,
    category_id: Optional[int] = None,
) -> tuple[list[Article], int]:
    """Retrieve a paginated, filtered list of articles.

    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        search: Optional substring to search in title or body (case-insensitive).
        status: Optional status to filter by exact match.
        author: Optional author name to filter by exact match.
        category_id: Optional category ID to filter articles belonging to that category.

    Returns:
        A tuple of (list of Article instances, total count before pagination).
    """
    query = db.query(Article)

    if search is not None:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.body.ilike(search_term),
            )
        )

    if status is not None:
        query = query.filter(Article.status == status)

    if author is not None:
        query = query.filter(Article.author == author)

    if category_id is not None:
        query = query.join(
            article_categories,
            Article.id == article_categories.c.article_id,
        ).filter(article_categories.c.category_id == category_id)

    total = query.count()

    offset = (page - 1) * per_page
    articles = query.offset(offset).limit(per_page).all()

    return articles, total


def update_article(
    db: Session, article_id: int, data: ArticleUpdate
) -> Optional[Article]:
    """Update an existing article.

    Args:
        db: Database session.
        article_id: Primary key of the article to update.
        data: Partial update data.

    Returns:
        The updated Article instance if found, else None.
    """
    from app.models.category import Category

    article = get_article(db, article_id)
    if article is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    category_ids = update_data.pop("category_ids", None)

    for field, value in update_data.items():
        setattr(article, field, value)

    if category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by its ID.

    Args:
        db: Database session.
        article_id: Primary key of the article to delete.

    Returns:
        True if the article was deleted, False if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
