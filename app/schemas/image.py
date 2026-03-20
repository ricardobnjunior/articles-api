"""Pydantic schemas for image responses."""

from pydantic import BaseModel


class ImageResponse(BaseModel):
    """Schema for image upload response.

    Attributes:
        filename: The stored filename on disk.
        url: The URL path to access the image.
        size: File size in bytes.
    """

    filename: str
    url: str
    size: int
