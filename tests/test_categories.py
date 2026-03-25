"""Tests for category CRUD endpoints and article-category relationships."""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_category(client: TestClient, name: str, description: str | None = None):
    """Helper to POST a new category and return the response."""
    payload: dict = {"name": name}
    if description is not None:
        payload["description"] = description
    return client.post("/api/v1/categories/", json=payload)


def _create_article(client: TestClient, category_ids: list[int] | None = None):
    """Helper to POST a new article and return the response."""
    payload = {
        "title": "Test Article",
        "body": "Body text.",
        "author": "Author Name",
        "status": "draft",
    }
    if category_ids is not None:
        payload["category_ids"] = category_ids
    return client.post("/api/v1/articles/", json=payload)


# ---------------------------------------------------------------------------
# Category creation tests
# ---------------------------------------------------------------------------

class TestCreateCategory:
    """Tests for POST /api/v1/categories/."""

    def test_create_category_returns_201(self, client: TestClient):
        """Creating a valid category returns HTTP 201."""
        resp = _create_category(client, "Technology", "Tech news")
        assert resp.status_code == 201

    def test_create_category_response_shape(self, client: TestClient):
        """Response includes id, name, slug, description."""
        resp = _create_category(client, "Science", "Science articles")
        data = resp.json()
        assert "id" in data
        assert data["name"] == "Science"
        assert data["slug"] == "science"
        assert data["description"] == "Science articles"

    def test_create_category_slug_simple(self, client: TestClient):
        """Simple single-word name produces lowercase slug."""
        resp = _create_category(client, "Sports")
        assert resp.json()["slug"] == "sports"

    def test_create_category_slug_multi_word(self, client: TestClient):
        """Multi-word name produces hyphen-separated slug."""
        resp = _create_category(client, "My Test Category")
        assert resp.json()["slug"] == "my-test-category"

    def test_create_category_slug_special_chars(self, client: TestClient):
        """Special characters are stripped from slug."""
        resp = _create_category(client, "Health & Wellness!")
        slug = resp.json()["slug"]
        assert "&" not in slug
        assert "!" not in slug
        assert "health" in slug

    def test_create_category_no_description(self, client: TestClient):
        """Category without description has null description."""
        resp = _create_category(client, "NullDesc")
        assert resp.json()["description"] is None

    def test_create_category_duplicate_name_returns_409(self, client: TestClient):
        """Creating a category with a duplicate name returns HTTP 409."""
        _create_category(client, "Duplicate")
        resp = _create_category(client, "Duplicate")
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Category retrieval tests
# ---------------------------------------------------------------------------

class TestGetCategory:
    """Tests for GET /api/v1/categories/{category_id}."""

    def test_get_existing_category(self, client: TestClient):
        """GET on existing category returns 200 with correct data."""
        created = _create_category(client, "GetMe").json()
        resp = client.get(f"/api/v1/categories/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "GetMe"

    def test_get_nonexistent_category_returns_404(self, client: TestClient):
        """GET on non-existent category returns 404."""
        resp = client.get("/api/v1/categories/999999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Category list tests
# ---------------------------------------------------------------------------

class TestListCategories:
    """Tests for GET /api/v1/categories/."""

    def test_list_categories_empty(self, client: TestClient):
        """List returns empty array when no categories exist."""
        resp = client.get("/api/v1/categories/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_categories_contains_created(self, client: TestClient):
        """All created categories appear in the list."""
        _create_category(client, "ListCat1")
        _create_category(client, "ListCat2")
        resp = client.get("/api/v1/categories/")
        names = [c["name"] for c in resp.json()]
        assert "ListCat1" in names
        assert "ListCat2" in names


# ---------------------------------------------------------------------------
# Category update tests
# ---------------------------------------------------------------------------

class TestUpdateCategory:
    """Tests for PUT /api/v1/categories/{category_id}."""

    def test_update_category_name(self, client: TestClient):
        """Updating the name also updates the slug."""
        created = _create_category(client, "OldName").json()
        resp = client.put(
            f"/api/v1/categories/{created['id']}",
            json={"name": "New Name"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New Name"
        assert data["slug"] == "new-name"

    def test_update_category_description(self, client: TestClient):
        """Updating description returns the new description."""
        created = _create_category(client, "UpdateDesc", "Old desc").json()
        resp = client.put(
            f"/api/v1/categories/{created['id']}",
            json={"description": "New desc"},
        )
        assert resp.status_code == 200
        assert resp.json()["description"] == "New desc"

    def test_update_nonexistent_category_returns_404(self, client: TestClient):
        """PUT on non-existent category returns 404."""
        resp = client.put("/api/v1/categories/999999", json={"name": "X"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Category delete tests
# ---------------------------------------------------------------------------

class TestDeleteCategory:
    """Tests for DELETE /api/v1/categories/{category_id}."""

    def test_delete_category_returns_204(self, client: TestClient):
        """Deleting an existing category returns 204."""
        created = _create_category(client, "DeleteMe").json()
        resp = client.delete(f"/api/v1/categories/{created['id']}")
        assert resp.status_code == 204

    def test_delete_category_then_get_returns_404(self, client: TestClient):
        """After deletion, GET on the same ID returns 404."""
        created = _create_category(client, "DeleteThenGet").json()
        client.delete(f"/api/v1/categories/{created['id']}")
        resp = client.get(f"/api/v1/categories/{created['id']}")
        assert resp.status_code == 404

    def test_delete_nonexistent_category_returns_404(self, client: TestClient):
        """Deleting a non-existent category returns 404."""
        resp = client.delete("/api/v1/categories/999999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Article-Category relationship tests
# ---------------------------------------------------------------------------

class TestArticleCategories:
    """Tests for article creation/update with category_ids."""

    def test_create_article_with_categories(self, client: TestClient):
        """Creating an article with category_ids populates categories in response."""
        cat1 = _create_category(client, "ArticleCat1").json()
        cat2 = _create_category(client, "ArticleCat2").json()
        resp = _create_article(client, category_ids=[cat1["id"], cat2["id"]])
        assert resp.status_code == 201
        data = resp.json()
        assert "categories" in data
        returned_ids = {c["id"] for c in data["categories"]}
        assert cat1["id"] in returned_ids
        assert cat2["id"] in returned_ids

    def test_create_article_without_categories(self, client: TestClient):
        """Creating an article without category_ids returns empty categories list."""
        resp = _create_article(client)
        assert resp.status_code == 201
        assert resp.json()["categories"] == []

    def test_update_article_categories(self, client: TestClient):
        """Updating an article's category_ids replaces the categories."""
        cat1 = _create_category(client, "UpdateCat1").json()
        cat2 = _create_category(client, "UpdateCat2").json()

        article = _create_article(client, category_ids=[cat1["id"]]).json()
        article_id = article["id"]

        resp = client.put(
            f"/api/v1/articles/{article_id}",
            json={"category_ids": [cat2["id"]]},
        )
        assert resp.status_code == 200
        data = resp.json()
        returned_ids = {c["id"] for c in data["categories"]}
        assert cat2["id"] in returned_ids
        assert cat1["id"] not in returned_ids

    def test_delete_category_does_not_delete_article(self, client: TestClient):
        """Deleting a category removes the association but not the article."""
        cat = _create_category(client, "CascadeCat").json()
        article = _create_article(client, category_ids=[cat["id"]]).json()
        article_id = article["id"]

        client.delete(f"/api/v1/categories/{cat['id']}")

        resp = client.get(f"/api/v1/articles/{article_id}")
        assert resp.status_code == 200
        assert resp.json()["categories"] == []

    def test_article_response_includes_category_fields(self, client: TestClient):
        """Categories in ArticleResponse include id, name, slug, description."""
        cat = _create_category(client, "FieldCheck", "desc").json()
        article = _create_article(client, category_ids=[cat["id"]]).json()
        cat_in_article = article["categories"][0]
        assert "id" in cat_in_article
        assert "name" in cat_in_article
        assert "slug" in cat_in_article
        assert "description" in cat_in_article
