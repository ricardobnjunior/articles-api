"""REST API endpoints for article management including image upload."""

import os

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
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
from app.models.article import ArticleStatus
from app.schemas.article import (
    ArticleCreate,
    ArticleList,
    ArticleResponse,
    ArticleUpdate,
    PaginationMeta,
)
from app.schemas.image import ImageResponse

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", response_model=ArticleList)
def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    status: ArticleStatus | None = Query(None),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> ArticleList:
    """List articles with optional filtering and pagination.

    Args:
        page: Page number (1-indexed).
        per_page: Number of articles per page.
        search: Optional full-text search string.
        status: Optional status filter.
        category_id: Optional category filter.
        db: Database session.

    Returns:
        Paginated list of articles.
    """
    articles, total = get_articles(
        db,
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        category_id=category_id,
    )
    pages = max(1, -(-total // per_page))  # ceiling division
    return ArticleList(
        items=articles,
        meta=PaginationMeta(total=total, page=page, per_page=per_page, pages=pages),
    )


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Create a new article.

    Args:
        article_in: Article creation data.
        db: Database session.

    Returns:
        The created article.
    """
    return create_article(db, article_in)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Retrieve a single article by ID.

    Args:
        article_id: The article's primary key.
        db: Database session.

    Returns:
        The requested article.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article_endpoint(
    article_id: int,
    article_in: ArticleUpdate,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Update an existing article.

    Args:
        article_id: The article's primary key.
        article_in: Fields to update.
        db: Database session.

    Returns:
        The updated article.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return update_article(db, article, article_in)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_endpoint(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an article.

    Args:
        article_id: The article's primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    delete_article(db, article)


@router.post(
    "/{article_id}/image",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_article_image(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ImageResponse:
    """Upload an image for an article.

    Saves the uploaded file to the configured upload directory and updates
    the article's image_url field.

    Args:
        article_id: The article's primary key.
        file: The uploaded image file.
        db: Database session.

    Returns:
        ImageResponse with filename, url, and file size.

    Raises:
        HTTPException: 404 if the article is not found.
        HTTPException: 400 if the file is not an image.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (content type must start with 'image/')",
        )

    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)

    filename = f"{article_id}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, filename)

    # Read file content to get size
    file_content = file.file.read()
    file_size = len(file_content)

    with open(file_path, "wb") as out_file:
        out_file.write(file_content)

    image_url = f"/uploads/{filename}"
    article.image_url = image_url
    db.commit()
    db.refresh(article)

    return ImageResponse(filename=filename, url=image_url, size=file_size)


@router.delete("/{article_id}/image", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_image(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete the image associated with an article.

    Removes the image file from disk and clears the article's image_url field.

    Args:
        article_id: The article's primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if the article is not found.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.image_url:
        settings = get_settings()
        # Derive file path from the URL: /uploads/{filename} → {upload_dir}/{filename}
        filename = os.path.basename(article.image_url)
        file_path = os.path.join(settings.upload_dir, filename)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass  # File already gone — proceed to clear the DB field

    article.image_url = None
    db.commit()
