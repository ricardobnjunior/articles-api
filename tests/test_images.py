"""Tests for article image upload and delete endpoints."""

import io
import os

import pytest
from fastapi.testclient import TestClient


def create_test_article(client: TestClient) -> dict:
    """Helper to create a test article and return its response data.

    Args:
        client: FastAPI TestClient instance.

    Returns:
        Dict containing the created article's data.
    """
    response = client.post(
        "/articles/",
        json={"title": "Test Article", "content": "Test content", "status": "draft"},
    )
    assert response.status_code == 201
    return response.json()


def make_image_file(filename: str = "test.jpg", content: bytes = b"fake-image-data") -> tuple:
    """Create an in-memory image file for upload testing.

    Args:
        filename: Name to use for the file.
        content: Byte content to use as file data.

    Returns:
        Tuple of (field_name, (filename, file_object, content_type)).
    """
    return ("file", (filename, io.BytesIO(content), "image/jpeg"))


def test_upload_image_success(client: TestClient) -> None:
    """Test successful image upload returns 201 with correct ImageResponse fields."""
    article = create_test_article(client)
    article_id = article["id"]

    image_content = b"\xff\xd8\xff\xe0" + b"fake-jpeg-data"
    files = {"file": ("photo.jpg", io.BytesIO(image_content), "image/jpeg")}

    response = client.post(f"/articles/{article_id}/image", files=files)

    assert response.status_code == 201
    data = response.json()
    assert "filename" in data
    assert "url" in data
    assert "size" in data
    assert data["filename"] == f"{article_id}_photo.jpg"
    assert data["url"] == f"/uploads/{article_id}_photo.jpg"
    assert data["size"] == len(image_content)


def test_upload_to_nonexistent_article(client: TestClient) -> None:
    """Test that uploading to a non-existent article returns 404."""
    files = {"file": ("photo.jpg", io.BytesIO(b"fake-image-data"), "image/jpeg")}

    response = client.post("/articles/99999/image", files=files)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_upload_non_image_file(client: TestClient) -> None:
    """Test that uploading a non-image file returns 400."""
    article = create_test_article(client)
    article_id = article["id"]

    files = {"file": ("document.txt", io.BytesIO(b"plain text content"), "text/plain")}

    response = client.post(f"/articles/{article_id}/image", files=files)

    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower()


def test_delete_image_success(client: TestClient) -> None:
    """Test successful image deletion returns 204 and clears image_url."""
    article = create_test_article(client)
    article_id = article["id"]

    # First upload an image
    files = {"file": ("photo.jpg", io.BytesIO(b"fake-image-data"), "image/jpeg")}
    upload_response = client.post(f"/articles/{article_id}/image", files=files)
    assert upload_response.status_code == 201

    # Delete the image
    delete_response = client.delete(f"/articles/{article_id}/image")
    assert delete_response.status_code == 204

    # Verify image_url is cleared
    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 200
    assert get_response.json()["image_url"] is None


def test_delete_image_nonexistent_article(client: TestClient) -> None:
    """Test that deleting image for a non-existent article returns 404."""
    response = client.delete("/articles/99999/image")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_image_url_in_article_response(client: TestClient) -> None:
    """Test that image_url appears correctly in article GET response after upload."""
    article = create_test_article(client)
    article_id = article["id"]

    # Verify image_url is initially None
    get_before = client.get(f"/articles/{article_id}")
    assert get_before.status_code == 200
    assert get_before.json()["image_url"] is None

    # Upload image
    image_content = b"fake-image-bytes"
    files = {"file": ("banner.png", io.BytesIO(image_content), "image/png")}
    upload_response = client.post(f"/articles/{article_id}/image", files=files)
    assert upload_response.status_code == 201

    # Verify image_url is set in article response
    get_after = client.get(f"/articles/{article_id}")
    assert get_after.status_code == 200
    article_data = get_after.json()
    assert article_data["image_url"] == f"/uploads/{article_id}_banner.png"


def test_upload_image_file_saved_to_disk(client: TestClient, override_upload_dir: str) -> None:
    """Test that uploaded image file is actually saved to the upload directory.

    Args:
        client: FastAPI TestClient instance.
        override_upload_dir: Path to the temporary upload directory.
    """
    article = create_test_article(client)
    article_id = article["id"]

    image_content = b"real-image-bytes"
    files = {"file": ("saved.jpg", io.BytesIO(image_content), "image/jpeg")}
    response = client.post(f"/articles/{article_id}/image", files=files)
    assert response.status_code == 201

    expected_file = os.path.join(override_upload_dir, f"{article_id}_saved.jpg")
    assert os.path.exists(expected_file)

    with open(expected_file, "rb") as f:
        assert f.read() == image_content


def test_upload_replaces_previous_image(client: TestClient) -> None:
    """Test that uploading a new image updates the article's image_url."""
    article = create_test_article(client)
    article_id = article["id"]

    # Upload first image
    files1 = {"file": ("first.jpg", io.BytesIO(b"first-image"), "image/jpeg")}
    r1 = client.post(f"/articles/{article_id}/image", files=files1)
    assert r1.status_code == 201

    # Upload second image
    files2 = {"file": ("second.jpg", io.BytesIO(b"second-image"), "image/jpeg")}
    r2 = client.post(f"/articles/{article_id}/image", files=files2)
    assert r2.status_code == 201

    # Article should now have the second image URL
    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 200
    assert get_response.json()["image_url"] == f"/uploads/{article_id}_second.jpg"


def test_delete_image_no_file_on_disk(client: TestClient) -> None:
    """Test that deleting image works even if file is not on disk."""
    article = create_test_article(client)
    article_id = article["id"]

    # Manually set image_url without creating a file
    update_response = client.put(
        f"/articles/{article_id}",
        json={"image_url": "/uploads/ghost_file.jpg"},
    )
    assert update_response.status_code == 200

    # Delete should succeed even if file doesn't exist
    delete_response = client.delete(f"/articles/{article_id}/image")
    assert delete_response.status_code == 204

    get_response = client.get(f"/articles/{article_id}")
    assert get_response.json()["image_url"] is None
