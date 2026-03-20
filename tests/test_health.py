"""Tests for the health check endpoint."""

from starlette.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """GET /health should return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body(client: TestClient) -> None:
    """GET /health should return status ok and include environment key."""
    response = client.get("/health")
    body = response.json()
    assert body["status"] == "ok"
    assert "environment" in body


def test_health_environment_value(client: TestClient) -> None:
    """GET /health environment field should be a non-empty string."""
    response = client.get("/health")
    body = response.json()
    assert isinstance(body["environment"], str)
    assert len(body["environment"]) > 0
