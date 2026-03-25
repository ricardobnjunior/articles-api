from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.article import (
    create_article,
    get_article,
    get_articles,
    update_article,
    delete_article
)
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_article_endpoint(data, db: Session = Depends(get_db)):
    try:
        article = create_article(db, data)
        return {"id": article.id, "title": article.title, "status": article.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{article_id}", response_model=dict)
def get_article_endpoint(article_id: int, db: Session = Depends(get_db)):
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "status": article.status,
        "created_at": article.created_at
    }

@router.get("/", response_model=dict)
def get_articles_endpoint(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    articles, total = get_articles(db, skip, limit)
    return {
        "articles": [
            {
                "id": a.id,
                "title": a.title,
                "status": a.status,
                "created_at": a.created_at
            } for a in articles
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.put("/{article_id}", response_model=dict)
def update_article_endpoint(article_id: int, data, db: Session = Depends(get_db)):
    article = update_article(db, article_id, data)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "status": article.status
    }

@router.delete("/{article_id}")
def delete_article_endpoint(article_id: int, db: Session = Depends(get_db)):
    success = delete_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully"}
