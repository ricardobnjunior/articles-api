"""REST endpoints for articles."""

import math
from typing import Optional

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
def create_article_endpoint(
    data: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article."""
    article = create_article(db, data)
    return article


@router.get("/", response_model=ArticleList)
def list_articles(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in title or body"),
    status: Optional[ArticleStatus] = Query(None, description="Filter by status"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with optional filtering, searching, and pagination."""
    articles, total = get_articles(
        db=db,
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        author=author,
        category_id=category_id,
    )

    pages = math.ceil(total / per_page) if per_page > 0 else 0

    meta = PaginationMeta(
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )

    return ArticleList(items=articles, meta=meta)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve a single article by ID."""
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article."""
    article = update_article(db, article_id, data)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}", status_code=204)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an article by ID."""
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
