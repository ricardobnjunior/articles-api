"""REST API endpoints for Article CRUD operations."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db
from app.schemas.article import ArticleCreate, ArticleList, ArticleResponse, ArticleUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    data: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        data: Validated article creation payload.
        db: Injected synchronous database session.

    Returns:
        The created article as an ArticleResponse.
    """
    article = create_article(db, data)
    return article  # type: ignore[return-value]


@router.get("", response_model=ArticleList)
def list_articles_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ArticleList:
    """Return a paginated list of articles.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return (1–100).
        db: Injected synchronous database session.

    Returns:
        An ArticleList containing items and total count.
    """
    items, total = get_articles(db, skip=skip, limit=limit)
    return ArticleList(items=items, total=total)  # type: ignore[arg-type]


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: Primary key of the article.
        db: Injected synchronous database session.

    Returns:
        The article as an ArticleResponse.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found.",
        )
    return article  # type: ignore[return-value]


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article by ID.

    Args:
        article_id: Primary key of the article to update.
        data: Validated article update payload.
        db: Injected synchronous database session.

    Returns:
        The updated article as an ArticleResponse.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = update_article(db, article_id, data)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found.",
        )
    return article  # type: ignore[return-value]


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an article by ID.

    Args:
        article_id: Primary key of the article to delete.
        db: Injected synchronous database session.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with id {article_id} not found.",
        )
