from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.article import Article, ArticleStatus

def create_article(db: Session, data) -> Article:
    db_article = Article(
        title=data.title,
        content=data.content,
        status=data.status if hasattr(data, 'status') else ArticleStatus.DRAFT
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_article(db: Session, article_id: int) -> Optional[Article]:
    return db.query(Article).filter(Article.id == article_id).first()

def get_articles(db: Session, skip: int = 0, limit: int = 20) -> Tuple[list[Article], int]:
    total = db.query(func.count(Article.id)).scalar()
    articles = db.query(Article).order_by(desc(Article.created_at)).offset(skip).limit(limit).all()
    return articles, total

def update_article(db: Session, article_id: int, data) -> Optional[Article]:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(article, key, value)
    db.commit()
    db.refresh(article)
    return article

def delete_article(db: Session, article_id: int) -> bool:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return False
    db.delete(article)
    db.commit()
    return True
