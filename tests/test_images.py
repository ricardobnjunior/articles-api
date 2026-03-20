"""Tests for image upload and delete endpoints."""

import io
import os

import pytest
from fastapi.testclient import TestClient


def create_article(client: TestClient) -> dict:
    """Helper to create a test article.

    Args:
        client: FastAPI TestClient.

    Returns:
        The created article data as a dict.
    """
    response = client.post(
        "/api/v1/articles/",
        json={"title": "Test Article", "content": "Test content", "status": "draft"},
    )
    assert response.status_code == 201
    return response.json()


def test_upload_image_success(client: TestClient) -> None:
    """Test that uploading a valid image returns 201 with correct fields."""
    article = create_article(client)
    article_id = article["id"]

    image_content = b"fake image content for testing"
    image_file = io.BytesIO(image_content)

    response = client.post(
        f"/api/v1/articles/{article_id}/image",
        files={"file": ("test_image.jpg", image_file, "image/jpeg")},
    )

    assert response.status_code == 201
    data = response.json()
    assert "filename" in data
    assert "url" in data
    assert "size" in data
    assert data["filename"] == f"{article_id}_test_image.jpg"
    assert data["url"] == f"/uploads/{article_id}_test_image.jpg"
    assert data["size"] == len(image_content)
    assert data["size"] > 0


def test_upload_image_article_not_found(client: TestClient) -> None:
    """Test that uploading to a non-existent article returns 404."""
    image_file = io.BytesIO(b"fake image content")

    response = client.post(
        "/api/v1/articles/99999/image",
        files={"file": ("test_image.jpg", image_file, "image/jpeg")},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_upload_non_image_returns_400(client: TestClient) -> None:
    """Test that uploading a non-image file returns 400."""
    article = create_article(client)
    article_id = article["id"]

    text_file = io.BytesIO(b"this is plain text content")

    response = client.post(
        f"/api/v1/articles/{article_id}/image",
        files={"file": ("document.txt", text_file, "text/plain")},
    )

    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower()


def test_delete_image_success(client: TestClient) -> None:
    """Test that deleting an image removes the file and returns 204."""
    from app.config import get_settings

    article = create_article(client)
    article_id = article["id"]

    # Upload image first
    image_content = b"fake image content"
    image_file = io.BytesIO(image_content)
    upload_response = client.post(
        f"/api/v1/articles/{article_id}/image",
        files={"file": ("test_delete.jpg", image_file, "image/jpeg")},
    )
    assert upload_response.status_code == 201

    # Verify file exists on disk
    settings = get_settings()
    filename = f"{article_id}_test_delete.jpg"
    file_path = os.path.join(settings.upload_dir, filename)
    assert os.path.exists(file_path), "File should exist after upload"

    # Delete the image
    delete_response = client.delete(f"/api/v1/articles/{article_id}/image")
    assert delete_response.status_code == 204

    # Verify file is removed from disk
    assert not os.path.exists(file_path), "File should be removed after delete"


def test_image_url_in_article_response(client: TestClient) -> None:
    """Test that image_url appears in article GET response after upload."""
    article = create_article(client)
    article_id = article["id"]

    # Initially image_url should be None
    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 200
    assert get_response.json()["image_url"] is None

    # Upload image
    image_file = io.BytesIO(b"fake image content for testing")
    upload_response = client.post(
        f"/api/v1/articles/{article_id}/image",
        files={"file": ("hero.png", image_file, "image/png")},
    )
    assert upload_response.status_code == 201

    # Now GET article and check image_url is set
    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 200
    article_data = get_response.json()
    assert article_data["image_url"] == f"/uploads/{article_id}_hero.png"


def test_delete_nonexistent_article_image(client: TestClient) -> None:
    """Test that deleting image from non-existent article returns 404."""
    response = client.delete("/api/v1/articles/99999/image")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_image_clears_image_url(client: TestClient) -> None:
    """Test that after deleting image, article image_url is None."""
    article = create_article(client)
    article_id = article["id"]

    # Upload image
    image_file = io.BytesIO(b"some image bytes")
    client.post(
        f"/api/v1/articles/{article_id}/image",
        files={"file": ("cover.jpg", image_file, "image/jpeg")},
    )

    # Delete image
    client.delete(f"/api/v1/articles/{article_id}/image")

    # Verify image_url is cleared
    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 200
    assert get_response.json()["image_url"] is None


def test_upload_overwrites_existing_image(client: TestClient) -> None:
    """Test that uploading a new image overwrites the previous image_url."""
    article = create_article(client)
    article_id = article["id"]

    # Upload first image
    client.post(
        f"/api/v1/articles/{article_id}/image",
        files={"file": ("first.jpg", io.BytesIO(b"first image"), "image/jpeg")},
    )

    # Upload second image
    response = client.post(
        f"/api/v1/articles/{article_id}/image",
        files={"file": ("second.jpg", io.BytesIO(b"second image"), "image/jpeg")},
    )
    assert response.status_code == 201

    # Verify article has the second image URL
    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.json()["image_url"] == f"/uploads/{article_id}_second.jpg"
