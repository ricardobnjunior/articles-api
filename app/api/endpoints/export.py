"""Export endpoint for bulk article download in CSV or JSON format."""

import csv
import io
import json
from datetime import datetime
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article

router = APIRouter()


def article_to_dict(article: Article) -> dict:
    """Convert an Article ORM instance to a plain dictionary.

    Args:
        article: The Article ORM instance to convert.

    Returns:
        A dictionary with all article fields. datetime fields are converted
        to ISO 8601 format strings.
    """
    result = {}
    for column in Article.__table__.columns:
        value = getattr(article, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result


def generate_csv_content(articles: list) -> str:
    """Generate CSV content from a list of Article instances.

    Args:
        articles: List of Article ORM instances.

    Returns:
        A string containing the CSV data with header row and one row per article.
    """
    buffer = io.StringIO()
    column_names = [column.name for column in Article.__table__.columns]
    writer = csv.writer(buffer)
    writer.writerow(column_names)
    for article in articles:
        article_dict = article_to_dict(article)
        writer.writerow([article_dict[col] for col in column_names])
    return buffer.getvalue()


def stream_csv(content: str) -> Generator[str, None, None]:
    """Yield CSV content as a single chunk for streaming.

    Args:
        content: The full CSV string content.

    Yields:
        The CSV content string.
    """
    yield content


@router.get("/articles")
def export_articles(
    format: str = Query(..., description="Export format: 'csv' or 'json'"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Export all articles as a downloadable CSV or JSON file.

    Args:
        format: The desired export format. Must be either 'csv' or 'json'.
        db: The database session dependency.

    Returns:
        A StreamingResponse containing the article data in the requested format.

    Raises:
        HTTPException: 400 if the format parameter is not 'csv' or 'json'.
    """
    if format not in ("csv", "json"):
        raise HTTPException(
            status_code=400,
            detail="Format must be 'csv' or 'json'",
        )

    articles = db.query(Article).all()

    if format == "csv":
        csv_content = generate_csv_content(articles)
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="articles.csv"'
            },
        )

    # JSON format
    article_dicts = [article_to_dict(article) for article in articles]
    json_content = json.dumps(article_dicts, default=str)
    return StreamingResponse(
        iter([json_content]),
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="articles.json"'
        },
    )
