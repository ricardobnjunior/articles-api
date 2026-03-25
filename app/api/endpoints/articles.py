"""REST endpoints for the Article resource."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
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


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    data: ArticleCreate, db: Session = Depends(get_db)
) -> ArticleResponse:
    """Create a new article.

    Args:
        data: Validated article creation payload.
        db: Injected database session.

    Returns:
        The created article.
    """
    article = create_article(db, data)
    return article


@router.get("/", response_model=ArticleList)
def list_articles_endpoint(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
) -> ArticleList:
    """List articles with optional pagination.

    Args:
        skip: Number of articles to skip.
        limit: Maximum number of articles to return.
        db: Injected database session.

    Returns:
        Paginated list of articles and total count.
    """
    items, total = get_articles(db, skip=skip, limit=limit)
    return ArticleList(items=items, total=total)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int, db: Session = Depends(get_db)
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: Primary key of the article.
        db: Injected database session.

    Returns:
        The article if found.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found",
        )
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int, data: ArticleUpdate, db: Session = Depends(get_db)
) -> ArticleResponse:
    """Update an existing article.

    Args:
        article_id: Primary key of the article to update.
        data: Fields to update (all optional).
        db: Injected database session.

    Returns:
        The updated article.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    article = update_article(db, article_id, data)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found",
        )
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_endpoint(
    article_id: int, db: Session = Depends(get_db)
) -> Response:
    """Delete an article by ID.

    Args:
        article_id: Primary key of the article to delete.
        db: Injected database session.

    Returns:
        Empty 204 response on success.

    Raises:
        HTTPException: 404 if the article does not exist.
    """
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
