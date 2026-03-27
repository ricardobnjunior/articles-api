"""Tests for Article CRUD endpoints."""

import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Return a Starlette TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def article(client: TestClient) -> dict:
    """Create a test article and return the response body."""
    payload = {
        "title": "Test Article",
        "body": "This is the body of the test article.",
        "author": "Jane Doe",
        "status": "draft",
    }
    response = client.post("/api/v1/articles/", json=payload)
    assert response.status_code == 201
    return response.json()


class TestCreateArticle:
    """Tests for POST /api/v1/articles/."""

    def test_create_article_returns_201(self, client: TestClient) -> None:
        """Creating a valid article returns HTTP 201."""
        payload = {
            "title": "My Article",
            "body": "Body content here.",
            "author": "Alice",
        }
        response = client.post("/api/v1/articles/", json=payload)
        assert response.status_code == 201

    def test_create_article_response_fields(self, client: TestClient) -> None:
        """Created article response contains all expected fields."""
        payload = {
            "title": "Field Check",
            "body": "Checking fields.",
            "author": "Bob",
            "status": "draft",
        }
        response = client.post("/api/v1/articles/", json=payload)
        data = response.json()
        assert "id" in data
        assert data["title"] == "Field Check"
        assert data["body"] == "Checking fields."
        assert data["author"] == "Bob"
        assert data["status"] == "draft"
        assert "created_at" in data

    def test_create_article_with_published_status(self, client: TestClient) -> None:
        """Creating an article with status=published persists the status."""
        payload = {
            "title": "Published Article",
            "body": "Published body.",
            "author": "Carol",
            "status": "published",
        }
        response = client.post("/api/v1/articles/", json=payload)
        assert response.status_code == 201
        assert response.json()["status"] == "published"

    def test_create_article_default_status_is_draft(self, client: TestClient) -> None:
        """Creating an article without status defaults to draft."""
        payload = {
            "title": "Default Status",
            "body": "Some body.",
            "author": "Dave",
        }
        response = client.post("/api/v1/articles/", json=payload)
        assert response.status_code == 201
        assert response.json()["status"] == "draft"

    def test_create_article_missing_title_returns_422(self, client: TestClient) -> None:
        """Missing title returns HTTP 422 Unprocessable Entity."""
        payload = {"body": "No title here.", "author": "Eve"}
        response = client.post("/api/v1/articles/", json=payload)
        assert response.status_code == 422

    def test_create_article_missing_body_returns_422(self, client: TestClient) -> None:
        """Missing body returns HTTP 422 Unprocessable Entity."""
        payload = {"title": "No Body", "author": "Frank"}
        response = client.post("/api/v1/articles/", json=payload)
        assert response.status_code == 422

    def test_create_article_missing_author_returns_422(self, client: TestClient) -> None:
        """Missing author returns HTTP 422 Unprocessable Entity."""
        payload = {"title": "No Author", "body": "Some content."}
        response = client.post("/api/v1/articles/", json=payload)
        assert response.status_code == 422


class TestGetArticle:
    """Tests for GET /api/v1/articles/{article_id}."""

    def test_get_existing_article_returns_200(
        self, client: TestClient, article: dict
    ) -> None:
        """Retrieving an existing article returns HTTP 200."""
        article_id = article["id"]
        response = client.get(f"/api/v1/articles/{article_id}")
        assert response.status_code == 200

    def test_get_existing_article_correct_fields(
        self, client: TestClient, article: dict
    ) -> None:
        """Retrieved article has correct fields matching the created article."""
        article_id = article["id"]
        response = client.get(f"/api/v1/articles/{article_id}")
        data = response.json()
        assert data["id"] == article_id
        assert data["title"] == article["title"]
        assert data["body"] == article["body"]
        assert data["author"] == article["author"]

    def test_get_nonexistent_article_returns_404(self, client: TestClient) -> None:
        """Retrieving a non-existent article returns HTTP 404."""
        response = client.get("/api/v1/articles/999999")
        assert response.status_code == 404
        assert "detail" in response.json()


class TestListArticles:
    """Tests for GET /api/v1/articles/."""

    def test_list_articles_returns_200(self, client: TestClient, article: dict) -> None:
        """Listing articles returns HTTP 200."""
        response = client.get("/api/v1/articles/")
        assert response.status_code == 200

    def test_list_articles_response_shape(
        self, client: TestClient, article: dict
    ) -> None:
        """List response contains items list and total count."""
        response = client.get("/api/v1/articles/")
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)

    def test_list_articles_total_at_least_one(
        self, client: TestClient, article: dict
    ) -> None:
        """Total count is at least 1 after creating an article."""
        response = client.get("/api/v1/articles/")
        data = response.json()
        assert data["total"] >= 1

    def test_list_articles_limit_param(
        self, client: TestClient, article: dict
    ) -> None:
        """Limit param caps the number of returned items."""
        response = client.get("/api/v1/articles/?skip=0&limit=1")
        data = response.json()
        assert len(data["items"]) <= 1

    def test_list_articles_skip_param(self, client: TestClient, article: dict) -> None:
        """Skip and limit params are accepted without error."""
        response = client.get("/api/v1/articles/?skip=0&limit=5")
        assert response.status_code == 200


class TestUpdateArticle:
    """Tests for PUT /api/v1/articles/{article_id}."""

    def test_update_article_returns_200(
        self, client: TestClient, article: dict
    ) -> None:
        """Updating an existing article returns HTTP 200."""
        article_id = article["id"]
        response = client.put(
            f"/api/v1/articles/{article_id}", json={"title": "Updated Title"}
        )
        assert response.status_code == 200

    def test_update_article_changes_title(
        self, client: TestClient, article: dict
    ) -> None:
        """Updating title field changes the title in the response."""
        article_id = article["id"]
        response = client.put(
            f"/api/v1/articles/{article_id}", json={"title": "New Title"}
        )
        assert response.json()["title"] == "New Title"

    def test_update_article_preserves_other_fields(
        self, client: TestClient, article: dict
    ) -> None:
        """Partial update preserves fields not included in the payload."""
        article_id = article["id"]
        original_body = article["body"]
        response = client.put(
            f"/api/v1/articles/{article_id}", json={"title": "Changed Title Only"}
        )
        assert response.json()["body"] == original_body

    def test_update_article_status(self, client: TestClient, article: dict) -> None:
        """Updating status field changes the status in the response."""
        article_id = article["id"]
        response = client.put(
            f"/api/v1/articles/{article_id}", json={"status": "published"}
        )
        assert response.json()["status"] == "published"

    def test_update_nonexistent_article_returns_404(
        self, client: TestClient
    ) -> None:
        """Updating a non-existent article returns HTTP 404."""
        response = client.put(
            "/api/v1/articles/999999", json={"title": "Ghost Update"}
        )
        assert response.status_code == 404


class TestDeleteArticle:
    """Tests for DELETE /api/v1/articles/{article_id}."""

    def test_delete_article_returns_204(self, client: TestClient) -> None:
        """Deleting an existing article returns HTTP 204."""
        payload = {
            "title": "To Be Deleted",
            "body": "Delete me.",
            "author": "Ghost",
        }
        create_response = client.post("/api/v1/articles/", json=payload)
        assert create_response.status_code == 201
        article_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/articles/{article_id}")
        assert response.status_code == 204

    def test_delete_article_no_body(self, client: TestClient) -> None:
        """Deleted article response has no body content."""
        payload = {
            "title": "No Body Delete",
            "body": "Body here.",
            "author": "Nobody",
        }
        create_response = client.post("/api/v1/articles/", json=payload)
        article_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/articles/{article_id}")
        assert response.status_code == 204
        assert response.content == b""

    def test_delete_article_then_get_returns_404(self, client: TestClient) -> None:
        """Getting a deleted article returns HTTP 404."""
        payload = {
            "title": "Delete Then Get",
            "body": "Will be gone.",
            "author": "Houdini",
        }
        create_response = client.post("/api/v1/articles/", json=payload)
        article_id = create_response.json()["id"]

        client.delete(f"/api/v1/articles/{article_id}")
        response = client.get(f"/api/v1/articles/{article_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_article_returns_404(
        self, client: TestClient
    ) -> None:
        """Deleting a non-existent article returns HTTP 404."""
        response = client.delete("/api/v1/articles/999999")
        assert response.status_code == 404
