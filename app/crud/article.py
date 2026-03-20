"""CRUD operations for Article model."""

from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus
from app.models.category import Category
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article.

    Args:
        db: The database session.
        data: The article creation data.

    Returns:
        The newly created Article instance.
    """
    article = Article(
        title=data.title,
        body=data.body,
        author=data.author,
        status=ArticleStatus(data.status) if data.status else ArticleStatus.draft,
    )
    db.add(article)
    db.flush()  # Get the article ID without committing

    # Assign categories if provided
    if data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        article.categories = categories

    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve an article by its ID.

    Args:
        db: The database session.
        article_id: The ID of the article to retrieve.

    Returns:
        The Article instance, or None if not found.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(db: Session, skip: int = 0, limit: int = 20) -> tuple[list[Article], int]:
    """Retrieve a paginated list of articles with total count.

    Args:
        db: The database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A tuple of (list of Article instances, total count).
    """
    total = db.query(Article).count()
    articles = db.query(Article).offset(skip).limit(limit).all()
    return articles, total


def update_article(db: Session, article_id: int, data: ArticleUpdate) -> Article | None:
    """Update an existing article.

    Args:
        db: The database session.
        article_id: The ID of the article to update.
        data: The update data.

    Returns:
        The updated Article instance, or None if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return None

    if data.title is not None:
        article.title = data.title
    if data.body is not None:
        article.body = data.body
    if data.author is not None:
        article.author = data.author
    if data.status is not None:
        article.status = ArticleStatus(data.status)

    # Update categories if category_ids provided (including empty list to clear)
    if data.category_ids is not None:
        if data.category_ids:
            categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
            article.categories = categories
        else:
            article.categories = []

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by its ID.

    Args:
        db: The database session.
        article_id: The ID of the article to delete.

    Returns:
        True if the article was deleted, False if not found.
    """
    article = get_article(db, article_id)
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
