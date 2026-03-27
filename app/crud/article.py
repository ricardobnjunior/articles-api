"""CRUD operations for the Article model."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


def create_article(db: Session, data: ArticleCreate) -> Article:
    article = Article(**data.model_dump())
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int) -> Article | None:
    return db.get(Article, article_id)


def get_articles(
    db: Session, skip: int = 0, limit: int = 20
) -> tuple[list[Article], int]:
    total = db.scalar(select(func.count()).select_from(Article)) or 0
    articles = list(db.scalars(select(Article).offset(skip).limit(limit)).all())
    return articles, total


def update_article(
    db: Session, article_id: int, data: ArticleUpdate
) -> Article | None:
    article = db.get(Article, article_id)
    if article is None:
        return None

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


def delete_article(db: Session, article_id: int) -> bool:
    article = db.get(Article, article_id)
    if article is None:
        return False

    db.delete(article)
    db.commit()
    return True
