"""LLM-based category classifier using OpenRouter API."""

import json
from typing import TypedDict

from openai import OpenAI

from app.config import settings

SYSTEM_PROMPT = (
    "You are a content classifier. Given an article title and content, "
    "and a list of available categories, you must identify the most relevant "
    "categories for the article.\n\n"
    "Return your response as a JSON object with this exact structure:\n"
    '{"suggestions": [{"category_name": "<name>", "confidence": <float 0-1>}, ...]}\n\n'
    "Rules:\n"
    "- Only suggest categories from the provided list.\n"
    "- confidence must be a float between 0.0 and 1.0.\n"
    "- Sort suggestions by confidence descending.\n"
    "- Only include categories that are genuinely relevant to the article.\n"
    "- Return valid JSON only, no extra text."
)


class CategorySuggestion(TypedDict):
    """A category suggestion from the LLM classifier.

    Attributes:
        category_name: The name of the suggested category.
        confidence: Confidence score between 0.0 and 1.0.
    """

    category_name: str
    confidence: float


def suggest_categories(
    title: str,
    content: str,
    category_names: list[str],
    limit: int = 3,
) -> list[CategorySuggestion]:
    """Suggest categories for an article using an LLM via OpenRouter API.

    Sends the article title and content along with available category names
    to the configured LLM, which returns ranked category suggestions with
    confidence scores.

    Args:
        title: The article title.
        content: The article content/body.
        category_names: List of available category names to classify against.
        limit: Maximum number of suggestions to return. Defaults to 3.

    Returns:
        A list of CategorySuggestion dicts sorted by confidence descending,
        containing at most `limit` entries.

    Raises:
        Exception: Propagates any OpenAI/network errors to the caller.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    categories_str = ", ".join(category_names)
    user_message = (
        f"Article Title: {title}\n\n"
        f"Article Content:\n{content}\n\n"
        f"Available Categories: {categories_str}\n\n"
        "Please classify this article and return the most relevant categories."
    )

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)

    suggestions: list[CategorySuggestion] = []
    for item in data.get("suggestions", []):
        category_name = item.get("category_name", "")
        confidence = float(item.get("confidence", 0.0))
        if category_name and category_name in category_names:
            suggestions.append(
                CategorySuggestion(category_name=category_name, confidence=confidence)
            )

    suggestions.sort(key=lambda s: s["confidence"], reverse=True)
    return suggestions[:limit]
