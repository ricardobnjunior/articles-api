"""Tests conftest.py — fixtures for the tests package."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

import pytest  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from app.database import SessionLocal, create_tables  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all database tables once for the test session."""
    create_tables()


@pytest.fixture
def client() -> TestClient:
    """Return a Starlette TestClient for the FastAPI app.

    Returns:
        TestClient: A synchronous HTTP test client.
    """
    return TestClient(app)


@pytest.fixture
def db_session():
    """Yield a synchronous SQLAlchemy session for database testing.

    Yields:
        Session: A SQLAlchemy database session that is closed after the test.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
