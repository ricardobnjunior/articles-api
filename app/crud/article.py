"""CRUD operations for articles."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus, article_categories
from app.models.category import Category
from app.schemas.article import ArticleCreate, ArticleUpdate


def get_article(db: Session, article_id: int) -> Optional[Article]:
    """Retrieve a single article by ID.

    Args:
        db: Database session.
        article_id: Primary key of the article.

    Returns:
        The Article instance or None if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session,
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
) -> tuple:
    """Retrieve a paginated list of articles with optional filters.

    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        status: Optional status filter.
        search: Optional search string matched against title and content.
        category_id: Optional category ID filter.

    Returns:
        Tuple of (list of Article instances, total count).
    """
    query = db.query(Article)

    if status:
        query = query.filter(Article.status == status)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Article.title.ilike(search_term) | Article.content.ilike(search_term)
        )

    if category_id:
        query = query.filter(
            Article.categories.any(Category.id == category_id)
        )

    total = query.count()
    offset = (page - 1) * per_page
    articles = query.offset(offset).limit(per_page).all()

    return articles, total


def create_article(db: Session, article_data: ArticleCreate) -> Article:
    """Create a new article.

    Args:
        db: Database session.
        article_data: Validated article creation data.

    Returns:
        The newly created Article instance.
    """
    db_article = Article(
        title=article_data.title,
        content=article_data.content,
        status=article_data.status,
    )

    if article_data.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(article_data.category_ids)
        ).all()
        db_article.categories = categories

    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def update_article(
    db: Session, article_id: int, article_data: ArticleUpdate
) -> Optional[Article]:
    """Update an existing article.

    Args:
        db: Database session.
        article_id: Primary key of the article to update.
        article_data: Validated article update data.

    Returns:
        The updated Article instance or None if not found.
    """
    db_article = get_article(db, article_id)
    if not db_article:
        return None

    update_data = article_data.model_dump(exclude_unset=True)

    # Handle category_ids separately
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")
        if category_ids is not None:
            categories = db.query(Category).filter(
                Category.id.in_(category_ids)
            ).all()
            db_article.categories = categories
        else:
            db_article.categories = []

    # Apply remaining fields including image_url
    for field, value in update_data.items():
        setattr(db_article, field, value)

    db.commit()
    db.refresh(db_article)
    return db_article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by ID.

    Args:
        db: Database session.
        article_id: Primary key of the article to delete.

    Returns:
        True if the article was deleted, False if not found.
    """
    db_article = get_article(db, article_id)
    if not db_article:
        return False

    db.delete(db_article)
    db.commit()
    return True
