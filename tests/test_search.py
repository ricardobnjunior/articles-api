"""Tests for article search, filtering, and pagination."""

import math

import pytest

from app.models.article import Article, ArticleStatus
from app.models.category import Category


def make_article(db, title, body, author, status=ArticleStatus.draft, categories=None):
    """Helper to create an article in the test database.

    Args:
        db: Database session.
        title: Article title.
        body: Article body text.
        author: Author name.
        status: ArticleStatus value.
        categories: Optional list of Category instances.

    Returns:
        The created Article instance.
    """
    article = Article(
        title=title,
        body=body,
        author=author,
        status=status,
    )
    if categories:
        article.categories = categories
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def make_category(db, name):
    """Helper to create a category in the test database.

    Args:
        db: Database session.
        name: Category name.

    Returns:
        The created Category instance.
    """
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture()
def sample_data(db_session):
    """Create a set of articles and categories for search/filter tests.

    Args:
        db_session: Database session fixture.

    Returns:
        Dict with 'articles', 'cat_tech', 'cat_science' keys.
    """
    cat_tech = make_category(db_session, "Technology")
    cat_science = make_category(db_session, "Science")

    a1 = make_article(
        db_session,
        title="Python Programming Guide",
        body="Learn Python from scratch.",
        author="Alice",
        status=ArticleStatus.published,
        categories=[cat_tech],
    )
    a2 = make_article(
        db_session,
        title="Introduction to FastAPI",
        body="FastAPI is a modern web framework for Python.",
        author="Bob",
        status=ArticleStatus.published,
        categories=[cat_tech],
    )
    a3 = make_article(
        db_session,
        title="Draft Article About Space",
        body="Space exploration is fascinating.",
        author="Alice",
        status=ArticleStatus.draft,
        categories=[cat_science],
    )
    a4 = make_article(
        db_session,
        title="Quantum Physics Basics",
        body="An introduction to quantum mechanics.",
        author="Charlie",
        status=ArticleStatus.draft,
        categories=[cat_science],
    )
    a5 = make_article(
        db_session,
        title="Advanced Python Tips",
        body="Tips for experienced Python developers.",
        author="Bob",
        status=ArticleStatus.published,
        categories=[cat_tech, cat_science],
    )

    return {
        "articles": [a1, a2, a3, a4, a5],
        "cat_tech": cat_tech,
        "cat_science": cat_science,
    }


class TestSearchByTitle:
    """Tests for search functionality on article titles."""

    def test_search_by_title_substring(self, client, sample_data):
        """Search by title substring returns matching articles."""
        response = client.get("/api/v1/articles/", params={"search": "Python"})
        assert response.status_code == 200
        data = response.json()
        titles = [item["title"] for item in data["items"]]
        assert all("Python" in t for t in titles)
        assert len(titles) >= 2

    def test_search_by_body_substring(self, client, sample_data):
        """Search by body substring returns articles matching body content."""
        response = client.get("/api/v1/articles/", params={"search": "quantum mechanics"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Quantum Physics Basics"

    def test_search_case_insensitive(self, client, sample_data):
        """Search is case-insensitive (ilike)."""
        response_lower = client.get("/api/v1/articles/", params={"search": "python"})
        response_upper = client.get("/api/v1/articles/", params={"search": "PYTHON"})
        assert response_lower.status_code == 200
        assert response_upper.status_code == 200
        lower_ids = {item["id"] for item in response_lower.json()["items"]}
        upper_ids = {item["id"] for item in response_upper.json()["items"]}
        assert lower_ids == upper_ids
        assert len(lower_ids) >= 2

    def test_search_matches_title_and_body(self, client, sample_data):
        """Search matches articles where the term appears in title OR body."""
        # "Python" appears in title of a1 and a5, and in body of a2
        response = client.get("/api/v1/articles/", params={"search": "Python"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 3


class TestFilterByStatus:
    """Tests for filtering articles by status."""

    def test_filter_by_status_draft(self, client, sample_data):
        """Filter by status=draft returns only draft articles."""
        response = client.get("/api/v1/articles/", params={"status": "draft"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["status"] == "draft"

    def test_filter_by_status_published(self, client, sample_data):
        """Filter by status=published returns only published articles."""
        response = client.get("/api/v1/articles/", params={"status": "published"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        for item in data["items"]:
            assert item["status"] == "published"


class TestFilterByAuthor:
    """Tests for filtering articles by author."""

    def test_filter_by_author_alice(self, client, sample_data):
        """Filter by author=Alice returns only Alice's articles."""
        response = client.get("/api/v1/articles/", params={"author": "Alice"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["author"] == "Alice"

    def test_filter_by_author_bob(self, client, sample_data):
        """Filter by author=Bob returns only Bob's articles."""
        response = client.get("/api/v1/articles/", params={"author": "Bob"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["author"] == "Bob"

    def test_filter_by_author_charlie(self, client, sample_data):
        """Filter by author=Charlie returns only Charlie's articles."""
        response = client.get("/api/v1/articles/", params={"author": "Charlie"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["author"] == "Charlie"


class TestFilterByCategory:
    """Tests for filtering articles by category."""

    def test_filter_by_category_tech(self, client, sample_data):
        """Filter by category_id returns only articles in that category."""
        cat_id = sample_data["cat_tech"].id
        response = client.get("/api/v1/articles/", params={"category_id": cat_id})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3  # a1, a2, a5
        for item in data["items"]:
            category_ids = [c["id"] for c in item["categories"]]
            assert cat_id in category_ids

    def test_filter_by_category_science(self, client, sample_data):
        """Filter by science category returns only science articles."""
        cat_id = sample_data["cat_science"].id
        response = client.get("/api/v1/articles/", params={"category_id": cat_id})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3  # a3, a4, a5
        for item in data["items"]:
            category_ids = [c["id"] for c in item["categories"]]
            assert cat_id in category_ids


class TestPagination:
    """Tests for pagination functionality."""

    def test_pagination_page1(self, client, sample_data):
        """Page 1 with per_page=2 returns the first 2 items."""
        response = client.get("/api/v1/articles/", params={"page": 1, "per_page": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["meta"]["page"] == 1
        assert data["meta"]["per_page"] == 2

    def test_pagination_page2(self, client, sample_data):
        """Page 2 with per_page=2 returns different items than page 1."""
        resp1 = client.get("/api/v1/articles/", params={"page": 1, "per_page": 2})
        resp2 = client.get("/api/v1/articles/", params={"page": 2, "per_page": 2})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        ids_page1 = {item["id"] for item in resp1.json()["items"]}
        ids_page2 = {item["id"] for item in resp2.json()["items"]}
        assert ids_page1.isdisjoint(ids_page2)

    def test_pagination_meta_fields(self, client, sample_data):
        """Response includes all pagination meta fields with correct values."""
        response = client.get("/api/v1/articles/", params={"page": 1, "per_page": 2})
        assert response.status_code == 200
        meta = response.json()["meta"]
        assert "total" in meta
        assert "page" in meta
        assert "per_page" in meta
        assert "pages" in meta
        assert meta["total"] == 5
        assert meta["page"] == 1
        assert meta["per_page"] == 2
        assert meta["pages"] == 3  # ceil(5/2)

    def test_pagination_pages_calculation(self, client, sample_data):
        """meta.pages equals ceil(total / per_page)."""
        response = client.get("/api/v1/articles/", params={"page": 1, "per_page": 3})
        assert response.status_code == 200
        meta = response.json()["meta"]
        expected_pages = math.ceil(meta["total"] / meta["per_page"])
        assert meta["pages"] == expected_pages

    def test_pagination_last_page(self, client, sample_data):
        """Last page returns remaining items (may be fewer than per_page)."""
        response = client.get("/api/v1/articles/", params={"page": 3, "per_page": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1  # 5 items, page 3 of 2 = last 1

    def test_per_page_respected(self, client, sample_data):
        """per_page parameter limits the number of returned items."""
        response = client.get("/api/v1/articles/", params={"per_page": 3})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 3


class TestCombinedFilters:
    """Tests for combining multiple filters."""

    def test_combined_search_and_status(self, client, sample_data):
        """Combining search and status returns only matching published articles."""
        response = client.get(
            "/api/v1/articles/", params={"search": "Python", "status": "published"}
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["status"] == "published"
            assert (
                "python" in item["title"].lower() or "python" in item["body"].lower()
            )

    def test_combined_author_and_status(self, client, sample_data):
        """Combining author and status filters correctly."""
        response = client.get(
            "/api/v1/articles/", params={"author": "Alice", "status": "published"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["author"] == "Alice"
        assert data["items"][0]["status"] == "published"

    def test_combined_category_and_status(self, client, sample_data):
        """Combining category_id and status filters correctly."""
        cat_id = sample_data["cat_tech"].id
        response = client.get(
            "/api/v1/articles/",
            params={"category_id": cat_id, "status": "published"},
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["status"] == "published"
            category_ids = [c["id"] for c in item["categories"]]
            assert cat_id in category_ids


class TestEmptyResults:
    """Tests for queries that return no results."""

    def test_empty_results_no_match(self, client, sample_data):
        """Search with no matching results returns empty list with correct meta."""
        response = client.get(
            "/api/v1/articles/", params={"search": "xyznonexistentterm"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["page"] == 1

    def test_empty_results_meta_structure(self, client, sample_data):
        """Empty results still include full meta structure."""
        response = client.get(
            "/api/v1/articles/", params={"author": "NonExistentAuthor"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "meta" in data
        meta = data["meta"]
        assert meta["total"] == 0
        assert "page" in meta
        assert "per_page" in meta
        assert "pages" in meta

    def test_empty_results_no_articles(self, client, db_session):
        """With no articles at all, returns empty list and meta.total=0."""
        response = client.get("/api/v1/articles/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["meta"]["total"] == 0


class TestQueryValidation:
    """Tests for query parameter validation."""

    def test_per_page_zero_returns_422(self, client, sample_data):
        """per_page=0 is invalid and returns 422."""
        response = client.get("/api/v1/articles/", params={"per_page": 0})
        assert response.status_code == 422

    def test_per_page_over_100_returns_422(self, client, sample_data):
        """per_page=101 exceeds max and returns 422."""
        response = client.get("/api/v1/articles/", params={"per_page": 101})
        assert response.status_code == 422

    def test_page_zero_returns_422(self, client, sample_data):
        """page=0 is invalid and returns 422."""
        response = client.get("/api/v1/articles/", params={"page": 0})
        assert response.status_code == 422

    def test_valid_per_page_100(self, client, sample_data):
        """per_page=100 is valid (at the limit)."""
        response = client.get("/api/v1/articles/", params={"per_page": 100})
        assert response.status_code == 200

    def test_valid_page_1(self, client, sample_data):
        """page=1 is valid."""
        response = client.get("/api/v1/articles/", params={"page": 1})
        assert response.status_code == 200
