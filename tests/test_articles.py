"""Integration tests for the Article CRUD endpoints."""

import pytest
from starlette.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
    "title": "Hello World",
    "body": "This is the article body.",
    "author": "Jane Doe",
}


def create_article(client: TestClient, **overrides) -> dict:
    """Helper to POST a valid article and return the JSON response.

    Args:
        client: The test HTTP client.
        **overrides: Fields to override in the default payload.

    Returns:
        The JSON body of the 201 response.
    """
    payload = {**VALID_PAYLOAD, **overrides}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


def test_create_article_returns_201(client: TestClient) -> None:
    """POST /articles with valid payload returns 201 and the article data."""
    response = client.post("/api/v1/articles", json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == VALID_PAYLOAD["title"]
    assert data["body"] == VALID_PAYLOAD["body"]
    assert data["author"] == VALID_PAYLOAD["author"]
    assert data["status"] == "draft"
    assert "id" in data
    assert data["id"] is not None


def test_create_article_default_status_is_draft(client: TestClient) -> None:
    """POST /articles without status defaults to draft."""
    data = create_article(client)
    assert data["status"] == "draft"


def test_create_article_published_status(client: TestClient) -> None:
    """POST /articles with status=published stores published status."""
    data = create_article(client, status="published")
    assert data["status"] == "published"


def test_create_article_missing_title_returns_422(client: TestClient) -> None:
    """POST /articles without title returns 422 validation error."""
    payload = {"body": "body text", "author": "Author"}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 422


def test_create_article_missing_body_returns_422(client: TestClient) -> None:
    """POST /articles without body returns 422 validation error."""
    payload = {"title": "Title", "author": "Author"}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 422


def test_create_article_missing_author_returns_422(client: TestClient) -> None:
    """POST /articles without author returns 422 validation error."""
    payload = {"title": "Title", "body": "body text"}
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 422


def test_create_article_title_too_long_returns_422(client: TestClient) -> None:
    """POST /articles with title longer than 200 chars returns 422."""
    long_title = "A" * 201
    response = client.post(
        "/api/v1/articles",
        json={"title": long_title, "body": "body", "author": "Author"},
    )
    assert response.status_code == 422


def test_create_article_invalid_status_returns_422(client: TestClient) -> None:
    """POST /articles with an unrecognized status returns 422."""
    response = client.post(
        "/api/v1/articles",
        json={**VALID_PAYLOAD, "status": "archived"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Read single
# ---------------------------------------------------------------------------


def test_get_article_returns_200(client: TestClient) -> None:
    """GET /articles/{id} for an existing article returns 200 and the data."""
    created = create_article(client)
    article_id = created["id"]

    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == VALID_PAYLOAD["title"]


def test_get_article_not_found_returns_404(client: TestClient) -> None:
    """GET /articles/99999 for a non-existent article returns 404."""
    response = client.get("/api/v1/articles/99999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------


def test_list_articles_returns_200(client: TestClient) -> None:
    """GET /articles returns 200 with items and total."""
    create_article(client, title="Article 1")
    create_article(client, title="Article 2")

    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_list_articles_empty_db(client: TestClient) -> None:
    """GET /articles on an empty database returns total=0 and empty items."""
    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_articles_pagination(client: TestClient) -> None:
    """GET /articles with skip=1&limit=1 returns exactly 1 item but total=3."""
    create_article(client, title="Article A")
    create_article(client, title="Article B")
    create_article(client, title="Article C")

    response = client.get("/api/v1/articles?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 1


def test_list_articles_skip_beyond_total(client: TestClient) -> None:
    """GET /articles with skip beyond total returns empty items but correct total."""
    create_article(client)

    response = client.get("/api/v1/articles?skip=100&limit=20")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"] == []


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


def test_update_article_returns_200(client: TestClient) -> None:
    """PUT /articles/{id} with valid data returns 200 and updated fields."""
    created = create_article(client)
    article_id = created["id"]

    update_payload = {"title": "Updated Title", "status": "published"}
    response = client.put(f"/api/v1/articles/{article_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "published"
    # Body and author should remain unchanged
    assert data["body"] == VALID_PAYLOAD["body"]
    assert data["author"] == VALID_PAYLOAD["author"]


def test_partial_update_preserves_other_fields(client: TestClient) -> None:
    """PUT /articles/{id} with partial payload leaves untouched fields unchanged."""
    created = create_article(client)
    article_id = created["id"]

    response = client.put(f"/api/v1/articles/{article_id}", json={"body": "New body"})
    assert response.status_code == 200
    data = response.json()
    assert data["body"] == "New body"
    assert data["title"] == VALID_PAYLOAD["title"]
    assert data["author"] == VALID_PAYLOAD["author"]


def test_update_article_not_found_returns_404(client: TestClient) -> None:
    """PUT /articles/99999 for a non-existent article returns 404."""
    response = client.put("/api/v1/articles/99999", json={"title": "X"})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


def test_delete_article_returns_204(client: TestClient) -> None:
    """DELETE /articles/{id} for an existing article returns 204."""
    created = create_article(client)
    article_id = created["id"]

    response = client.delete(f"/api/v1/articles/{article_id}")
    assert response.status_code == 204


def test_delete_article_then_get_returns_404(client: TestClient) -> None:
    """After DELETE, subsequent GET on same article returns 404."""
    created = create_article(client)
    article_id = created["id"]

    client.delete(f"/api/v1/articles/{article_id}")

    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 404


def test_delete_article_not_found_returns_404(client: TestClient) -> None:
    """DELETE /articles/99999 for a non-existent article returns 404."""
    response = client.delete("/api/v1/articles/99999")
    assert response.status_code == 404
