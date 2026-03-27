"""Tests for Category CRUD endpoints and article-category relationships."""

import pytest
from starlette.testclient import TestClient


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def create_category_payload(name: str = "Tech", description: str = "Technology news"):
    """Return a category creation payload dict."""
    return {"name": name, "description": description}


def create_article_payload(
    title: str = "Test Article",
    body: str = "Article body text.",
    author: str = "Author Name",
    status: str = "draft",
    category_ids: list = None,
):
    """Return an article creation payload dict."""
    payload = {
        "title": title,
        "body": body,
        "author": author,
        "status": status,
    }
    if category_ids is not None:
        payload["category_ids"] = category_ids
    return payload


# ---------------------------------------------------------------------------
# Category creation
# ---------------------------------------------------------------------------

def test_create_category(client: TestClient):
    """POST /categories returns 201 with correct fields."""
    payload = create_category_payload(name="Science", description="Science articles")
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Science"
    assert data["description"] == "Science articles"
    assert "id" in data
    assert "slug" in data


def test_create_category_slug_auto_generated(client: TestClient):
    """Slug is auto-generated from the name when creating a category."""
    payload = create_category_payload(name="My Test Category")
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 201
    assert response.json()["slug"] == "my-test-category"


def test_create_category_slug_special_chars(client: TestClient):
    """Slug contains only alphanumeric characters and hyphens."""
    payload = create_category_payload(name="Hello & World!")
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 201
    slug = response.json()["slug"]
    # Slug should only contain a-z, 0-9, and hyphens, no leading/trailing hyphens
    assert slug == slug.strip("-")
    assert all(c.isalnum() or c == "-" for c in slug)


def test_duplicate_category_name_returns_409(client: TestClient):
    """POST with a duplicate category name returns 409 Conflict."""
    payload = create_category_payload(name="Unique Name")
    client.post("/api/v1/categories", json=payload)
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 409


# ---------------------------------------------------------------------------
# Category retrieval
# ---------------------------------------------------------------------------

def test_get_categories_empty(client: TestClient):
    """GET /categories returns an empty list when no categories exist."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert response.json() == []


def test_get_categories(client: TestClient):
    """GET /categories returns all created categories."""
    client.post("/api/v1/categories", json=create_category_payload("Cat A"))
    client.post("/api/v1/categories", json=create_category_payload("Cat B"))
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_category_by_id(client: TestClient):
    """GET /categories/{id} returns the correct category."""
    created = client.post(
        "/api/v1/categories", json=create_category_payload("Physics")
    ).json()
    response = client.get(f"/api/v1/categories/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == "Physics"
    assert data["slug"] == "physics"


def test_get_category_not_found(client: TestClient):
    """GET /categories/{id} returns 404 for a non-existent ID."""
    response = client.get("/api/v1/categories/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Category update
# ---------------------------------------------------------------------------

def test_update_category(client: TestClient):
    """PUT /categories/{id} updates the category and regenerates slug."""
    created = client.post(
        "/api/v1/categories", json=create_category_payload("Old Name")
    ).json()
    response = client.put(
        f"/api/v1/categories/{created['id']}",
        json={"name": "New Name", "description": "Updated desc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["slug"] == "new-name"
    assert data["description"] == "Updated desc"


def test_update_category_not_found(client: TestClient):
    """PUT /categories/{id} returns 404 for a non-existent ID."""
    response = client.put(
        "/api/v1/categories/9999", json={"name": "Anything"}
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Category deletion
# ---------------------------------------------------------------------------

def test_delete_category(client: TestClient):
    """DELETE /categories/{id} returns 204 and category is no longer accessible."""
    created = client.post(
        "/api/v1/categories", json=create_category_payload("To Delete")
    ).json()
    delete_response = client.delete(f"/api/v1/categories/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/categories/{created['id']}")
    assert get_response.status_code == 404


def test_delete_category_not_found(client: TestClient):
    """DELETE /categories/{id} returns 404 for a non-existent ID."""
    response = client.delete("/api/v1/categories/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Article + category relationship
# ---------------------------------------------------------------------------

def test_create_article_without_category_ids(client: TestClient):
    """POST /articles without category_ids returns empty categories list."""
    payload = create_article_payload(title="No Categories Article")
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["categories"] == []


def test_create_article_with_category_ids(client: TestClient):
    """POST /articles with category_ids returns associated categories."""
    cat = client.post(
        "/api/v1/categories", json=create_category_payload("Python")
    ).json()

    payload = create_article_payload(
        title="Python Article", category_ids=[cat["id"]]
    )
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert len(data["categories"]) == 1
    assert data["categories"][0]["id"] == cat["id"]
    assert data["categories"][0]["name"] == "Python"


def test_create_article_with_multiple_category_ids(client: TestClient):
    """POST /articles with multiple category_ids associates all categories."""
    cat1 = client.post(
        "/api/v1/categories", json=create_category_payload("Backend")
    ).json()
    cat2 = client.post(
        "/api/v1/categories", json=create_category_payload("Frontend")
    ).json()

    payload = create_article_payload(
        title="Full-Stack Article", category_ids=[cat1["id"], cat2["id"]]
    )
    response = client.post("/api/v1/articles", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert len(data["categories"]) == 2
    returned_ids = {c["id"] for c in data["categories"]}
    assert returned_ids == {cat1["id"], cat2["id"]}


def test_update_article_category_ids(client: TestClient):
    """PUT /articles/{id} with category_ids updates the category associations."""
    cat1 = client.post(
        "/api/v1/categories", json=create_category_payload("OldCat")
    ).json()
    cat2 = client.post(
        "/api/v1/categories", json=create_category_payload("NewCat")
    ).json()

    article = client.post(
        "/api/v1/articles",
        json=create_article_payload(title="Update Me", category_ids=[cat1["id"]]),
    ).json()

    response = client.put(
        f"/api/v1/articles/{article['id']}",
        json={"category_ids": [cat2["id"]]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["categories"]) == 1
    assert data["categories"][0]["id"] == cat2["id"]


def test_update_article_clear_categories(client: TestClient):
    """PUT /articles/{id} with empty category_ids clears all categories."""
    cat = client.post(
        "/api/v1/categories", json=create_category_payload("ToClear")
    ).json()

    article = client.post(
        "/api/v1/articles",
        json=create_article_payload(title="Clear Me", category_ids=[cat["id"]]),
    ).json()
    assert len(article["categories"]) == 1

    response = client.put(
        f"/api/v1/articles/{article['id']}",
        json={"category_ids": []},
    )
    assert response.status_code == 200
    assert response.json()["categories"] == []
