"""Root-level pytest configuration and shared fixtures."""

import os

# Set test environment variables BEFORE importing any app modules.
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ENVIRONMENT", "testing")

import pytest  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, create_tables, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
    """Create all database tables once for the test session.

    Yields:
        None
    """
    create_tables()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Session:
    """Yield a SQLAlchemy Session for use in tests.

    Yields:
        Session: An active sync SQLAlchemy session that is closed after the test.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> TestClient:
    """Yield a Starlette TestClient wrapping the FastAPI application.

    Yields:
        TestClient: A synchronous HTTP test client.
    """
    with TestClient(app) as test_client:
        yield test_client
