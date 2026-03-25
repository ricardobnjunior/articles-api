"""API endpoints for articles."""

import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db
from app.models.article import ArticleStatus
from app.schemas.article import (
    ArticleCreate,
    ArticleList,
    ArticleResponse,
    ArticleUpdate,
    PaginationMeta,
)

router = APIRouter()


@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article_endpoint(data: ArticleCreate, db: Session = Depends(get_db)):
    """Create a new article.

    Args:
        data: Article creation payload.
        db: Database session.

    Returns:
        The created article.
    """
    return create_article(db, data)


@router.get("/", response_model=ArticleList)
def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    status: ArticleStatus | None = Query(None),
    author: str | None = Query(None),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """List articles with optional search, filtering, and pagination.

    Args:
        page: Page number (1-indexed, must be >= 1).
        per_page: Items per page (1–100).
        search: Optional substring search on title or body (case-insensitive).
        status: Optional status filter (draft/published).
        author: Optional exact author filter.
        category_id: Optional category ID filter.
        db: Database session.

    Returns:
        Paginated list of articles with pagination metadata.
    """
    articles, total = get_articles(
        db=db,
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        author=author,
        category_id=category_id,
    )
    pages = math.ceil(total / per_page) if total > 0 else 1
    return ArticleList(
        items=articles,
        meta=PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(article_id: int, db: Session = Depends(get_db)):
    """Get a single article by ID.

    Args:
        article_id: The article's primary key.
        db: Database session.

    Returns:
        The article if found.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int, data: ArticleUpdate, db: Session = Depends(get_db)
):
    """Update an existing article.

    Args:
        article_id: The article's primary key.
        data: Article update payload.
        db: Database session.

    Returns:
        The updated article.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = update_article(db, article_id, data)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}", status_code=204)
def delete_article_endpoint(article_id: int, db: Session = Depends(get_db)):
    """Delete an article by ID.

    Args:
        article_id: The article's primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if article not found.
    """
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
