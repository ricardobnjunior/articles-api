"""Pydantic schemas for image upload responses."""

from pydantic import BaseModel


class ImageResponse(BaseModel):
    """Schema for image upload API response.

    Attributes:
        filename: The stored filename of the uploaded image.
        url: The URL path to access the uploaded image.
        size: File size in bytes.
    """

    filename: str
    url: str
    size: int
