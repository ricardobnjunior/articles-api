"""Pytest configuration and fixtures."""
import os
from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from app.database import Base, get_db

# Set environment variables BEFORE importing any app modules that use Settings
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("CORS_ORIGINS_STR", '["http://localhost:3000"]')

# Override get_db dependency for testing
engine = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database session for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a database session for tests.

    Yields:
        Database session.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a test client for API requests.

    Args:
        db_session: Database session fixture.

    Yields:
        TestClient instance.
    """
    # Create tables for each test
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    # Drop tables after each test
    Base.metadata.drop_all(bind=engine)
