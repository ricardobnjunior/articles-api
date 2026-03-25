"""Endpoint for AI-powered category suggestions."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.classifier import suggest_categories
from app.crud.article import get_article
from app.database import get_db
from app.models.category import Category

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


class CategorySuggestionResponse(BaseModel):
    """A single category suggestion with confidence score.

    Attributes:
        category_id: The database ID of the suggested category.
        category_name: The human-readable name of the category.
        confidence: Confidence score between 0.0 and 1.0.
    """

    category_id: int
    category_name: str
    confidence: float


class SuggestionsResponse(BaseModel):
    """Response model for the category suggestions endpoint.

    Attributes:
        article_id: The ID of the article that was classified.
        suggestions: Ordered list of category suggestions with scores.
    """

    article_id: int
    suggestions: list[CategorySuggestionResponse]


@router.get("/categories/{article_id}", response_model=SuggestionsResponse)
def get_category_suggestions(
    article_id: int,
    limit: int = Query(default=3, ge=1, description="Maximum number of suggestions to return"),
    db: Session = Depends(get_db),
) -> SuggestionsResponse:
    """Get AI-powered category suggestions for an article.

    Loads the article and all existing categories from the database, then
    calls the LLM classifier to suggest the most relevant categories with
    confidence scores.

    Args:
        article_id: The ID of the article to classify.
        limit: Maximum number of category suggestions to return (default 3).
        db: SQLAlchemy database session injected by FastAPI.

    Returns:
        SuggestionsResponse with article_id and list of category suggestions.

    Raises:
        HTTPException 404: If the article does not exist.
        HTTPException 500: If the LLM API call fails.
    """
    article = get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    categories = db.query(Category).all()
    if not categories:
        return SuggestionsResponse(article_id=article_id, suggestions=[])

    category_name_to_id: dict[str, int] = {cat.name: cat.id for cat in categories}
    category_names = list(category_name_to_id.keys())

    try:
        raw_suggestions = suggest_categories(
            title=article.title,
            content=article.content or "",
            category_names=category_names,
            limit=limit,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM classification failed: {exc}",
        ) from exc

    suggestions: list[CategorySuggestionResponse] = []
    for suggestion in raw_suggestions:
        cat_name = suggestion["category_name"]
        if cat_name in category_name_to_id:
            suggestions.append(
                CategorySuggestionResponse(
                    category_id=category_name_to_id[cat_name],
                    category_name=cat_name,
                    confidence=suggestion["confidence"],
                )
            )

    return SuggestionsResponse(article_id=article_id, suggestions=suggestions)
