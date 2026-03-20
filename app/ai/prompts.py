"""Prompt templates for the AI classifier."""

SYSTEM_PROMPT = (
    "You are a content classifier. Given an article title and content, "
    "and a list of available category names, you must identify which categories "
    "best match the article.\n\n"
    "Return ONLY a JSON object in this exact format, with no additional text:\n"
    '{"suggestions": [{"category_name": "CategoryName", "confidence": 0.85}, ...]}\n\n'
    "Rules:\n"
    "- confidence must be a float between 0.0 and 1.0\n"
    "- Only suggest categories from the provided list\n"
    "- Sort suggestions by confidence descending\n"
    "- Return only categories with confidence > 0.1\n"
    "- If no category matches well, return an empty suggestions list"
)

USER_PROMPT_TEMPLATE = (
    "Article Title: {title}\n\n"
    "Article Content:\n{content}\n\n"
    "Available Categories:\n{categories}\n\n"
    "Classify this article into the most relevant categories from the list above."
)
