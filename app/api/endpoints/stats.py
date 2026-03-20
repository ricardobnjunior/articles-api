"""Statistics and analytics endpoints for articles."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.models.category import Category, article_categories
from app.schemas.stats import (
    CategoryStat,
    LatestArticle,
    StatsResponse,
    TimelineEntry,
    TimelineResponse,
)

router = APIRouter()


@router.get("/", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    """Return aggregated statistics about articles.

    Args:
        db: SQLAlchemy database session injected via dependency.

    Returns:
        StatsResponse containing total counts, status breakdown,
        category breakdown, and the latest article summary.
    """
    # Total article count
    total_articles: int = db.query(func.count(Article.id)).scalar() or 0

    # Status breakdown: {status_value: count}
    status_rows = (
        db.query(Article.status, func.count(Article.id))
        .group_by(Article.status)
        .all()
    )
    by_status = {str(status): count for status, count in status_rows}

    # Category breakdown: join article_categories with Category, group by category
    category_rows = (
        db.query(
            Category.id,
            Category.name,
            func.count(article_categories.c.article_id).label("article_count"),
        )
        .join(article_categories, Category.id == article_categories.c.category_id)
        .group_by(Category.id, Category.name)
        .all()
    )
    by_category: List[CategoryStat] = [
        CategoryStat(
            category_id=row.id,
            category_name=row.name,
            article_count=row.article_count,
        )
        for row in category_rows
    ]

    # Total categories count (all categories, including those with no articles)
    total_categories: int = db.query(func.count(Category.id)).scalar() or 0

    # Latest article by created_at descending
    latest_row = db.query(Article).order_by(Article.created_at.desc()).first()
    latest_article = None
    if latest_row is not None:
        latest_article = LatestArticle(
            id=latest_row.id,
            title=latest_row.title,
            created_at=latest_row.created_at,
        )

    return StatsResponse(
        total_articles=total_articles,
        by_status=by_status,
        by_category=by_category,
        total_categories=total_categories,
        latest_article=latest_article,
    )


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(db: Session = Depends(get_db)) -> TimelineResponse:
    """Return a monthly timeline of article creation counts.

    Args:
        db: SQLAlchemy database session injected via dependency.

    Returns:
        TimelineResponse containing a list of month/count entries
        ordered chronologically (oldest to newest).
    """
    month_label = func.strftime("%Y-%m", Article.created_at).label("month")

    rows = (
        db.query(month_label, func.count(Article.id).label("count"))
        .group_by(month_label)
        .order_by(month_label)
        .all()
    )

    timeline: List[TimelineEntry] = [
        TimelineEntry(month=row.month, count=row.count) for row in rows
    ]

    return TimelineResponse(timeline=timeline)
