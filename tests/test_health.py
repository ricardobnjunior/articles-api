"""
Tests for health check endpoint.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test GET /health returns 200 with correct structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert data["environment"] in ["development", "testing", "production"]


def test_health_endpoint_structure():
    """Test health endpoint response structure."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data, dict)
    assert set(data.keys()) == {"status", "environment"}
    assert data["status"] == "ok"
