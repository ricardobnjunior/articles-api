"""CRUD operations for the Article model."""

from sqlalchemy.orm import Session

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    """Create a new article in the database.

    Args:
        db: SQLAlchemy database session.
        data: Validated article creation data.

    Returns:
        The newly created Article instance.
    """
    article = Article(
        title=data.title,
        body=data.body,
        author=data.author,
        status=data.status,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    """Retrieve a single article by its ID.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to retrieve.

    Returns:
        The Article instance if found, otherwise None.
    """
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session, skip: int = 0, limit: int = 20
) -> tuple[list[Article], int]:
    """Retrieve a paginated list of articles and the total count.

    Args:
        db: SQLAlchemy database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        A tuple of (list of Article instances, total count of articles).
    """
    query = db.query(Article)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def update_article(
    db: Session, article_id: int, data: ArticleUpdate
) -> Article | None:
    """Update an existing article with the provided fields.

    Only fields explicitly set (non-None) in `data` are updated.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to update.
        data: Validated article update data.

    Returns:
        The updated Article instance if found, otherwise None.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    """Delete an article by its ID.

    Args:
        db: SQLAlchemy database session.
        article_id: Primary key of the article to delete.

    Returns:
        True if the article was found and deleted, False if not found.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
