"""Tests for article search, filtering, and pagination."""

import pytest
from fastapi.testclient import TestClient


BASE_URL = "/api/v1/articles"


def make_article(
    title: str = "Test Article",
    body: str = "Test body content",
    author: str = "Author One",
    status: str = "draft",
    category_ids: list = None,
) -> dict:
    """Build an article creation payload.

    Args:
        title: Article title.
        body: Article body text.
        author: Author name.
        status: Article status string.
        category_ids: List of category IDs to assign.

    Returns:
        Dictionary payload for POST request.
    """
    payload = {
        "title": title,
        "body": body,
        "author": author,
        "status": status,
        "category_ids": category_ids or [],
    }
    return payload


def create_article(client: TestClient, **kwargs) -> dict:
    """Create an article via the API and return the response data.

    Args:
        client: FastAPI TestClient.
        **kwargs: Fields passed to make_article().

    Returns:
        Created article response dict.
    """
    payload = make_article(**kwargs)
    response = client.post(BASE_URL + "/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def create_category(client: TestClient, name: str, slug: str) -> dict:
    """Create a category via the API.

    Args:
        client: FastAPI TestClient.
        name: Category name.
        slug: URL slug for the category.

    Returns:
        Created category response dict.
    """
    response = client.post("/api/v1/categories/", json={"name": name, "slug": slug})
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------


def test_search_by_title(client: TestClient):
    """Search returns only articles matching the title substring."""
    create_article(client, title="Python Tutorial", body="Learn Python basics")
    create_article(client, title="Django Guide", body="Build web apps")

    response = client.get(BASE_URL + "/", params={"search": "Python"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] >= 1
    titles = [a["title"] for a in data["items"]]
    assert all("python" in t.lower() or "python" in t for t in titles)
    # Django Guide should NOT be in results
    assert not any("Django" in t for t in titles)


def test_search_by_body(client: TestClient):
    """Search returns articles matching the body substring (not title)."""
    create_article(client, title="Unique Title Alpha", body="Contains secretword here")
    create_article(client, title="Unique Title Beta", body="Different content entirely")

    response = client.get(BASE_URL + "/", params={"search": "secretword"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] >= 1
    titles = [a["title"] for a in data["items"]]
    assert "Unique Title Alpha" in titles
    assert "Unique Title Beta" not in titles


def test_search_case_insensitive(client: TestClient):
    """Search is case-insensitive."""
    create_article(client, title="CaseSensitive Article", body="body text")

    # Search with different case
    response = client.get(BASE_URL + "/", params={"search": "casesensitive"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] >= 1
    titles = [a["title"] for a in data["items"]]
    assert "CaseSensitive Article" in titles


def test_search_no_match(client: TestClient):
    """Search with no matching keyword returns empty items."""
    create_article(client, title="Normal Article", body="Normal body")

    response = client.get(BASE_URL + "/", params={"search": "xyzabcnonexistent123"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 0
    assert data["items"] == []


# ---------------------------------------------------------------------------
# Filter by status tests
# ---------------------------------------------------------------------------


def test_filter_by_status_draft(client: TestClient):
    """Filter by status=draft returns only draft articles."""
    create_article(client, title="Draft One", status="draft")
    create_article(client, title="Published One", status="published")

    response = client.get(BASE_URL + "/", params={"status": "draft"})
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "draft"


def test_filter_by_status_published(client: TestClient):
    """Filter by status=published returns only published articles."""
    create_article(client, title="Draft Two", status="draft")
    create_article(client, title="Published Two", status="published")

    response = client.get(BASE_URL + "/", params={"status": "published"})
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "published"


# ---------------------------------------------------------------------------
# Filter by author tests
# ---------------------------------------------------------------------------


def test_filter_by_author(client: TestClient):
    """Filter by author returns only articles by that author."""
    create_article(client, title="Alice Article 1", author="Alice")
    create_article(client, title="Alice Article 2", author="Alice")
    create_article(client, title="Bob Article 1", author="Bob")

    response = client.get(BASE_URL + "/", params={"author": "Alice"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] >= 2
    for item in data["items"]:
        assert item["author"] == "Alice"


def test_filter_by_author_no_match(client: TestClient):
    """Filter by unknown author returns empty results."""
    create_article(client, title="Some Article", author="Charlie")

    response = client.get(BASE_URL + "/", params={"author": "NonExistentAuthor"})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 0
    assert data["items"] == []


# ---------------------------------------------------------------------------
# Filter by category tests
# ---------------------------------------------------------------------------


def test_filter_by_category_id(client: TestClient):
    """Filter by category_id returns only articles in that category."""
    cat1 = create_category(client, name="Technology", slug="technology")
    cat2 = create_category(client, name="Science", slug="science")

    art1 = create_article(
        client,
        title="Tech Article",
        body="About technology",
        category_ids=[cat1["id"]],
    )
    art2 = create_article(
        client,
        title="Science Article",
        body="About science",
        category_ids=[cat2["id"]],
    )
    create_article(
        client,
        title="Uncategorized Article",
        body="No category",
        category_ids=[],
    )

    response = client.get(BASE_URL + "/", params={"category_id": cat1["id"]})
    assert response.status_code == 200
    data = response.json()
    ids = [a["id"] for a in data["items"]]
    assert art1["id"] in ids
    assert art2["id"] not in ids


def test_filter_by_category_no_articles(client: TestClient):
    """Filter by category with no articles returns empty results."""
    cat = create_category(client, name="EmptyCat", slug="empty-cat")

    response = client.get(BASE_URL + "/", params={"category_id": cat["id"]})
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 0
    assert data["items"] == []


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------


def test_pagination_page1(client: TestClient):
    """Page 1 returns the first batch of items."""
    for i in range(5):
        create_article(client, title=f"Page Article {i}", author="Paginator")

    response = client.get(BASE_URL + "/", params={"author": "Paginator", "page": 1, "per_page": 2})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["meta"]["page"] == 1
    assert data["meta"]["per_page"] == 2


def test_pagination_page2(client: TestClient):
    """Page 2 returns different items than page 1."""
    for i in range(5):
        create_article(client, title=f"Paginate2 Article {i}", author="Paginator2")

    resp1 = client.get(BASE_URL + "/", params={"author": "Paginator2", "page": 1, "per_page": 2})
    resp2 = client.get(BASE_URL + "/", params={"author": "Paginator2", "page": 2, "per_page": 2})

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    ids_page1 = {a["id"] for a in resp1.json()["items"]}
    ids_page2 = {a["id"] for a in resp2.json()["items"]}

    assert len(ids_page2) > 0
    assert ids_page1.isdisjoint(ids_page2), "Pages should not overlap"


def test_pagination_meta_fields(client: TestClient):
    """Response includes all required pagination meta fields."""
    create_article(client, title="Meta Test Article", author="MetaAuthor")

    response = client.get(BASE_URL + "/", params={"author": "MetaAuthor"})
    assert response.status_code == 200
    data = response.json()
    meta = data["meta"]
    assert "total" in meta
    assert "page" in meta
    assert "per_page" in meta
    assert "pages" in meta


def test_pagination_pages_calculation(client: TestClient):
    """With 5 articles and per_page=2, meta.pages should be 3."""
    for i in range(5):
        create_article(client, title=f"Pages Calc {i}", author="PagesCalcAuthor")

    response = client.get(
        BASE_URL + "/",
        params={"author": "PagesCalcAuthor", "page": 1, "per_page": 2},
    )
    assert response.status_code == 200
    data = response.json()
    meta = data["meta"]
    assert meta["total"] == 5
    assert meta["pages"] == 3


def test_pagination_last_page_partial(client: TestClient):
    """Last page may have fewer items than per_page."""
    for i in range(3):
        create_article(client, title=f"Partial Page {i}", author="PartialAuthor")

    response = client.get(
        BASE_URL + "/",
        params={"author": "PartialAuthor", "page": 2, "per_page": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["meta"]["total"] == 3
    assert data["meta"]["pages"] == 2


# ---------------------------------------------------------------------------
# Combined filter tests
# ---------------------------------------------------------------------------


def test_combined_search_and_status(client: TestClient):
    """Combined search + status filter narrows results correctly."""
    create_article(
        client,
        title="Combined Draft",
        body="special keyword here",
        status="draft",
        author="CombinedAuthor",
    )
    create_article(
        client,
        title="Combined Published",
        body="special keyword here",
        status="published",
        author="CombinedAuthor",
    )
    create_article(
        client,
        title="No Match Published",
        body="completely different",
        status="published",
        author="CombinedAuthor",
    )

    response = client.get(
        BASE_URL + "/",
        params={"search": "special keyword", "status": "published", "author": "CombinedAuthor"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["title"] == "Combined Published"


def test_combined_author_and_category(client: TestClient):
    """Combined author + category_id filter works correctly."""
    cat = create_category(client, name="Combined Cat", slug="combined-cat")

    art1 = create_article(
        client,
        title="Author Cat Match",
        author="SpecialAuthor",
        category_ids=[cat["id"]],
    )
    # Same author but different category
    create_article(client, title="Author No Cat", author="SpecialAuthor", category_ids=[])
    # Same category but different author
    create_article(
        client,
        title="Cat No Author",
        author="OtherAuthor",
        category_ids=[cat["id"]],
    )

    response = client.get(
        BASE_URL + "/",
        params={"author": "SpecialAuthor", "category_id": cat["id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] == 1
    assert data["items"][0]["id"] == art1["id"]


# ---------------------------------------------------------------------------
# Empty results tests
# ---------------------------------------------------------------------------


def test_empty_results_meta(client: TestClient):
    """Empty results return correct meta with total=0."""
    response = client.get(BASE_URL + "/", params={"author": "NoSuchAuthorEver999"})
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["total"] == 0
    assert data["meta"]["page"] == 1
    assert data["meta"]["pages"] == 0


def test_no_filters_returns_all(client: TestClient):
    """No filters returns all articles with valid pagination meta."""
    create_article(client, title="No Filter One", author="NFAuthor")
    create_article(client, title="No Filter Two", author="NFAuthor")

    response = client.get(BASE_URL + "/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    assert data["meta"]["total"] >= 2
    assert data["meta"]["page"] == 1
    assert data["meta"]["per_page"] == 20
    assert data["meta"]["pages"] >= 1
