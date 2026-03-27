"""REST API endpoints for Article resources."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db
from app.schemas.article import ArticleCreate, ArticleResponse, ArticleUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    data: ArticleCreate, db: Session = Depends(get_db)
) -> ArticleResponse:
    """Create a new article.

    Args:
        data: Article creation payload.
        db: Database session dependency.

    Returns:
        The newly created article.
    """
    return create_article(db, data)


@router.get("/", response_model=List[ArticleResponse])
def list_articles_endpoint(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
) -> List[ArticleResponse]:
    """Retrieve a paginated list of articles.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Database session dependency.

    Returns:
        A list of articles.
    """
    return get_articles(db, skip=skip, limit=limit)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int, db: Session = Depends(get_db)
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: The article's primary key.
        db: Database session dependency.

    Returns:
        The requested article.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int, data: ArticleUpdate, db: Session = Depends(get_db)
) -> ArticleResponse:
    """Update an existing article.

    Args:
        article_id: The article's primary key.
        data: Fields to update.
        db: Database session dependency.

    Returns:
        The updated article.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = update_article(db, article_id, data)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_endpoint(
    article_id: int, db: Session = Depends(get_db)
) -> None:
    """Delete an article by ID.

    Args:
        article_id: The article's primary key.
        db: Database session dependency.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
