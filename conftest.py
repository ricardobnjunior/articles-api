"""Pytest configuration and shared fixtures."""

import os

# Set required environment variables BEFORE importing any app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///./test_app.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database() -> None:
    """Create all tables before each test and drop them after."""
    # Import models to ensure they are registered with Base.metadata
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database: None) -> Session:
    """Provide a transactional database session for tests.

    Args:
        setup_database: Fixture that ensures tables exist.

    Yields:
        A SQLAlchemy Session instance.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(setup_database: None) -> TestClient:
    """Provide a FastAPI TestClient with overridden database dependency.

    Args:
        setup_database: Fixture that ensures tables exist.

    Yields:
        A configured TestClient instance.
    """
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
