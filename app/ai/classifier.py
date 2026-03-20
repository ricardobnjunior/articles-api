"""LLM-based article category classifier using OpenRouter API."""

import json
import logging
from typing import Any

from openai import OpenAI

from app.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.config import settings

logger = logging.getLogger(__name__)


def classify_article(
    title: str,
    content: str,
    category_names: list[str],
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Classify an article into categories using an LLM via OpenRouter.

    Sends the article title and content along with the list of available
    category names to the configured LLM. Parses the JSON response and
    returns the top suggestions sorted by confidence descending.

    Args:
        title: The article title.
        content: The article body text.
        category_names: List of available category names to choose from.
        limit: Maximum number of suggestions to return.

    Returns:
        A list of dicts, each with keys ``category_name`` (str) and
        ``confidence`` (float), sorted by confidence descending, limited
        to ``limit`` items.

    Raises:
        RuntimeError: If the LLM API call fails or returns unparseable JSON.
    """
    if not category_names:
        return []

    categories_str = "\n".join(f"- {name}" for name in category_names)
    user_message = USER_PROMPT_TEMPLATE.format(
        title=title,
        content=content,
        categories=categories_str,
    )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    try:
        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        logger.error("OpenRouter API call failed: %s", exc)
        raise RuntimeError(f"LLM API call failed: {exc}") from exc

    raw_content = response.choices[0].message.content

    try:
        data = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Failed to parse LLM response as JSON: %r", raw_content)
        raise RuntimeError(f"LLM returned invalid JSON: {exc}") from exc

    raw_suggestions = data.get("suggestions", [])

    if not isinstance(raw_suggestions, list):
        logger.error("Unexpected LLM response structure: %r", data)
        raise RuntimeError("LLM response has unexpected structure")

    valid_suggestions: list[dict[str, Any]] = []
    category_name_set = set(category_names)

    for item in raw_suggestions:
        if not isinstance(item, dict):
            continue
        cat_name = item.get("category_name")
        confidence = item.get("confidence")
        if not isinstance(cat_name, str) or cat_name not in category_name_set:
            continue
        if not isinstance(confidence, (int, float)):
            continue
        valid_suggestions.append(
            {"category_name": cat_name, "confidence": float(confidence)}
        )

    valid_suggestions.sort(key=lambda x: x["confidence"], reverse=True)
    return valid_suggestions[:limit]
