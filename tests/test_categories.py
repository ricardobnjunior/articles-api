"""Tests for Category endpoints and Article-Category integration."""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Category CRUD tests
# ---------------------------------------------------------------------------


def test_create_category(client: TestClient) -> None:
    """Test creating a category returns 201 with correct fields."""
    payload = {"name": "Technology", "description": "Tech articles"}
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Technology"
    assert data["description"] == "Tech articles"
    assert "id" in data
    assert "slug" in data


def test_create_category_duplicate_name(client: TestClient) -> None:
    """Test that creating a category with a duplicate name returns 409."""
    payload = {"name": "Duplicate Category"}
    client.post("/api/v1/categories", json=payload)
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 409


def test_slug_auto_generated_from_name(client: TestClient) -> None:
    """Test that a slug is auto-generated from the category name."""
    payload = {"name": "My Test Category"}
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "my-test-category"


def test_slug_handles_special_chars(client: TestClient) -> None:
    """Test that slugs are properly generated from names with special characters."""
    payload = {"name": "Python & Django!"}
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 201
    data = response.json()
    # Slug should be lowercase alphanumeric with hyphens only
    slug = data["slug"]
    assert slug == slug.lower()
    assert " " not in slug
    assert "!" not in slug
    assert "&" not in slug


def test_get_categories(client: TestClient) -> None:
    """Test listing categories returns 200 with a list."""
    client.post("/api/v1/categories", json={"name": "Science"})
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [c["name"] for c in data]
    assert "Science" in names


def test_get_category_by_id(client: TestClient) -> None:
    """Test retrieving a category by ID returns 200 with correct data."""
    create_resp = client.post("/api/v1/categories", json={"name": "History", "description": "Historical"})
    category_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "History"
    assert data["description"] == "Historical"


def test_get_category_not_found(client: TestClient) -> None:
    """Test retrieving a non-existent category returns 404."""
    response = client.get("/api/v1/categories/9999")
    assert response.status_code == 404


def test_update_category(client: TestClient) -> None:
    """Test updating a category returns 200 with updated fields and regenerated slug."""
    create_resp = client.post("/api/v1/categories", json={"name": "Old Name"})
    category_id = create_resp.json()["id"]

    update_resp = client.put(f"/api/v1/categories/{category_id}", json={"name": "New Name"})
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "New Name"
    assert data["slug"] == "new-name"


def test_update_category_not_found(client: TestClient) -> None:
    """Test updating a non-existent category returns 404."""
    response = client.put("/api/v1/categories/9999", json={"name": "Ghost"})
    assert response.status_code == 404


def test_update_category_duplicate_name_conflict(client: TestClient) -> None:
    """Test updating a category with a name that belongs to another returns 409."""
    client.post("/api/v1/categories", json={"name": "Alpha"})
    resp_b = client.post("/api/v1/categories", json={"name": "Beta"})
    category_b_id = resp_b.json()["id"]

    response = client.put(f"/api/v1/categories/{category_b_id}", json={"name": "Alpha"})
    assert response.status_code == 409


def test_delete_category(client: TestClient) -> None:
    """Test deleting a category returns 204 and subsequent GET returns 404."""
    create_resp = client.post("/api/v1/categories", json={"name": "To Delete"})
    category_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/categories/{category_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/v1/categories/{category_id}")
    assert get_resp.status_code == 404


def test_delete_category_not_found(client: TestClient) -> None:
    """Test deleting a non-existent category returns 404."""
    response = client.delete("/api/v1/categories/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Article-Category integration tests
# ---------------------------------------------------------------------------


def _create_article(client: TestClient, category_ids: list[int] | None = None) -> dict:
    """Helper to create an article via the API."""
    payload = {
        "title": "Integration Article",
        "body": "Article body content.",
        "author": "Test Author",
        "status": "draft",
    }
    if category_ids is not None:
        payload["category_ids"] = category_ids
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_article_with_category_ids(client: TestClient) -> None:
    """Test creating an article with category_ids links the categories."""
    cat_resp = client.post("/api/v1/categories", json={"name": "Linked Category"})
    category_id = cat_resp.json()["id"]

    article = _create_article(client, category_ids=[category_id])
    assert "categories" in article
    assert len(article["categories"]) == 1
    assert article["categories"][0]["id"] == category_id
    assert article["categories"][0]["name"] == "Linked Category"


def test_create_article_without_category_ids(client: TestClient) -> None:
    """Test creating an article without category_ids returns empty categories list."""
    article = _create_article(client)
    assert "categories" in article
    assert article["categories"] == []


def test_update_article_category_ids(client: TestClient) -> None:
    """Test updating an article's category_ids updates the relationship."""
    cat1_resp = client.post("/api/v1/categories", json={"name": "Cat One"})
    cat1_id = cat1_resp.json()["id"]
    cat2_resp = client.post("/api/v1/categories", json={"name": "Cat Two"})
    cat2_id = cat2_resp.json()["id"]

    article = _create_article(client, category_ids=[cat1_id])
    article_id = article["id"]
    assert len(article["categories"]) == 1

    update_resp = client.put(
        f"/api/v1/articles/{article_id}",
        json={"category_ids": [cat2_id]},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    category_ids_in_response = [c["id"] for c in updated["categories"]]
    assert cat2_id in category_ids_in_response
    assert cat1_id not in category_ids_in_response


def test_delete_category_removes_association(client: TestClient) -> None:
    """Test deleting a category removes the association but not the article."""
    cat_resp = client.post("/api/v1/categories", json={"name": "Ephemeral Category"})
    category_id = cat_resp.json()["id"]

    article = _create_article(client, category_ids=[category_id])
    article_id = article["id"]
    assert len(article["categories"]) == 1

    # Delete the category
    delete_resp = client.delete(f"/api/v1/categories/{category_id}")
    assert delete_resp.status_code == 204

    # Article still exists
    get_resp = client.get(f"/api/v1/articles/{article_id}")
    assert get_resp.status_code == 200
    # Categories association should be cleared
    assert get_resp.json()["categories"] == []


def test_article_response_includes_categories_field(client: TestClient) -> None:
    """Test that ArticleResponse always includes the categories field."""
    article = _create_article(client)
    assert "categories" in article
    assert isinstance(article["categories"], list)
