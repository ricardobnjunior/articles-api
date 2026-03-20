"""Root conftest — sets up environment variables and shared test fixtures."""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["ENVIRONMENT"] = "testing"

from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

# Use a file-based SQLite DB for tests to avoid in-memory isolation issues
TEST_DATABASE_URL = "sqlite:///./test_temp.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch app.database BEFORE importing app modules that use it
import app.database as _app_database  # noqa: E402

_app_database.engine = test_engine
_app_database.SessionLocal = TestingSessionLocal

# Now import models to register them with Base
import app.models  # noqa: F401, E402

from app.database import Base, get_db  # noqa: E402

# Now import the app (create_tables will use the patched engine)
from app.main import app  # noqa: E402


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh DB session for each test."""
    # Drop and recreate all tables for a clean slate
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Return a TestClient with the DB dependency overridden."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
