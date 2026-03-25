"""REST API endpoints for articles, including image upload/delete."""

import os
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.crud.article import (
    create_article,
    delete_article,
    get_article,
    get_articles,
    update_article,
)
from app.database import get_db
from app.schemas.article import (
    ArticleCreate,
    ArticleList,
    ArticleResponse,
    ArticleUpdate,
    PaginationMeta,
)
from app.schemas.image import ImageResponse

router = APIRouter()


@router.get("/", response_model=ArticleList)
def list_articles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with pagination, filtering, and search.

    Args:
        page: Page number (1-indexed).
        per_page: Number of items per page.
        status: Optional status filter.
        search: Optional search term.
        category_id: Optional category filter.
        db: Database session.

    Returns:
        Paginated list of articles with metadata.
    """
    articles, total = get_articles(
        db,
        page=page,
        per_page=per_page,
        status=status,
        search=search,
        category_id=category_id,
    )
    pages = ceil(total / per_page) if total > 0 else 1

    return ArticleList(
        items=articles,
        meta=PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article_endpoint(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        article_data: Article creation payload.
        db: Database session.

    Returns:
        The created article.
    """
    return create_article(db, article_data)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: Article primary key.
        db: Database session.

    Returns:
        The article data.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article.

    Args:
        article_id: Article primary key.
        article_data: Article update payload.
        db: Database session.

    Returns:
        The updated article.

    Raises:
        HTTPException: 404 if article not found.
    """
    article = update_article(db, article_id, article_data)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}", status_code=204)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an article by ID.

    Args:
        article_id: Article primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if article not found.
    """
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")


@router.post("/{article_id}/image", response_model=ImageResponse, status_code=201)
def upload_article_image(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ImageResponse:
    """Upload an image for an article.

    Saves the uploaded file to the configured upload directory and updates
    the article's image_url field.

    Args:
        article_id: Article primary key.
        file: Uploaded image file.
        db: Database session.

    Returns:
        ImageResponse with filename, URL, and file size.

    Raises:
        HTTPException: 404 if article not found.
        HTTPException: 400 if the uploaded file is not an image.
    """
    settings = get_settings()

    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be an image",
        )

    original_filename = file.filename or "upload"
    stored_filename = f"{article_id}_{original_filename}"
    file_path = os.path.join(settings.upload_dir, stored_filename)

    os.makedirs(settings.upload_dir, exist_ok=True)

    file_content = file.file.read()
    file_size = len(file_content)

    with open(file_path, "wb") as f:
        f.write(file_content)

    image_url = f"/uploads/{stored_filename}"
    article.image_url = image_url
    db.commit()
    db.refresh(article)

    return ImageResponse(
        filename=stored_filename,
        url=image_url,
        size=file_size,
    )


@router.delete("/{article_id}/image", status_code=204)
def delete_article_image(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete the image associated with an article.

    Removes the image file from disk and clears the article's image_url field.

    Args:
        article_id: Article primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if article not found.
    """
    settings = get_settings()

    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.image_url:
        # Extract filename from URL path: /uploads/{filename}
        stored_filename = article.image_url.split("/uploads/", 1)[-1]
        file_path = os.path.join(settings.upload_dir, stored_filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    article.image_url = None
    db.commit()
