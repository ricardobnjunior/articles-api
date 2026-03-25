"""Tests for the /health endpoint."""


def test_health_returns_200(client) -> None:
    """GET /health should return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_status_ok(client) -> None:
    """GET /health response body should contain status: ok."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_contains_environment(client) -> None:
    """GET /health response body should contain a non-empty environment field."""
    response = client.get("/health")
    data = response.json()
    assert "environment" in data
    assert isinstance(data["environment"], str)
    assert len(data["environment"]) > 0
