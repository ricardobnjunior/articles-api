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
    article = create_article(db, data)
    return article


@router.get("/", response_model=ArticleList)
def list_articles_endpoint(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
) -> ArticleList:
    articles, total = get_articles(db, skip=skip, limit=limit)
    return ArticleList(items=articles, total=total)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article_endpoint(
    article_id: int, db: Session = Depends(get_db)
) -> ArticleResponse:
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
    deleted = delete_article(db, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
