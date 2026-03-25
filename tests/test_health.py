"""Tests for the /health endpoint."""

from starlette.testclient import TestClient


def test_health_status_code(client: TestClient) -> None:
    """GET /health should return HTTP 200.

    Args:
        client: The test HTTP client fixture.
    """
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body_status(client: TestClient) -> None:
    """GET /health should return status 'ok' in the response body.

    Args:
        client: The test HTTP client fixture.
    """
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_response_body_environment(client: TestClient) -> None:
    """GET /health should return a non-empty environment string.

    Args:
        client: The test HTTP client fixture.
    """
    response = client.get("/health")
    data = response.json()
    assert "environment" in data
    assert isinstance(data["environment"], str)
    assert data["environment"] != ""


def test_health_full_response_shape(client: TestClient) -> None:
    """GET /health response JSON should contain exactly 'status' and 'environment' keys.

    Args:
        client: The test HTTP client fixture.
    """
    response = client.get("/health")
    data = response.json()
    assert set(data.keys()) == {"status", "environment"}
