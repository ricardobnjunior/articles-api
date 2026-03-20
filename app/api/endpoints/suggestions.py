"""API endpoint for AI-powered article category suggestions."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.classifier import classify_article
from app.crud.article import get_article
from app.database import get_db
from app.models.category import Category

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


class CategorySuggestionItem(BaseModel):
    """A single category suggestion with confidence score.

    Attributes:
        category_id: The database ID of the suggested category.
        category_name: The name of the suggested category.
        confidence: Confidence score between 0.0 and 1.0.
    """

    category_id: int
    category_name: str
    confidence: float


class CategorySuggestionsResponse(BaseModel):
    """Response model for category suggestions endpoint.

    Attributes:
        article_id: The ID of the article that was classified.
        suggestions: List of category suggestions sorted by confidence.
    """

    article_id: int
    suggestions: list[CategorySuggestionItem]


@router.get(
    "/categories/{article_id}",
    response_model=CategorySuggestionsResponse,
    summary="Get AI category suggestions for an article",
)
def get_category_suggestions(
    article_id: int,
    limit: int = 3,
    db: Session = Depends(get_db),
) -> CategorySuggestionsResponse:
    """Return AI-generated category suggestions for the given article.

    Fetches the article and all existing categories from the database,
    then sends them to the configured LLM to obtain category suggestions
    with confidence scores.

    Args:
        article_id: The ID of the article to classify.
        limit: Maximum number of suggestions to return (default: 3).
        db: SQLAlchemy database session (injected).

    Returns:
        A ``CategorySuggestionsResponse`` containing the article ID and
        a list of category suggestions.

    Raises:
        HTTPException 404: If the article does not exist.
        HTTPException 500: If the LLM call fails.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    categories = db.query(Category).all()

    if not categories:
        return CategorySuggestionsResponse(article_id=article_id, suggestions=[])

    category_name_to_id: dict[str, int] = {cat.name: cat.id for cat in categories}
    category_names = list(category_name_to_id.keys())

    try:
        raw_suggestions = classify_article(
            title=article.title,
            content=article.content or "",
            category_names=category_names,
            limit=limit,
        )
    except RuntimeError as exc:
        logger.error("Classifier failed for article %d: %s", article_id, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    suggestion_items: list[CategorySuggestionItem] = []
    for suggestion in raw_suggestions:
        cat_name = suggestion["category_name"]
        cat_id = category_name_to_id.get(cat_name)
        if cat_id is None:
            continue
        suggestion_items.append(
            CategorySuggestionItem(
                category_id=cat_id,
                category_name=cat_name,
                confidence=suggestion["confidence"],
            )
        )

    return CategorySuggestionsResponse(
        article_id=article_id,
        suggestions=suggestion_items,
    )
