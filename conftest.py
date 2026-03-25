"""Root conftest.py — sets environment variables before importing app modules."""

import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

from sqlalchemy.orm import Session  # noqa: E402

from app.database import SessionLocal, create_tables  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> None:
    """Create all tables once for the test session."""
    create_tables()


@pytest.fixture
def client():
    """Return a Starlette TestClient for the FastAPI app.

    Yields:
        TestClient: Synchronous HTTP test client.
    """
    from starlette.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """Yield a SQLAlchemy sync Session connected to the test database.

    Yields:
        Session: Active database session, closed after the test.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
