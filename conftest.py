"""Root-level pytest configuration and shared fixtures."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

# Import app modules only after env vars are set
from app.database import Base, SessionLocal, create_tables, engine  # noqa: E402
from app.main import app  # noqa: E402

import pytest  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once before the test session and drop them after.

    Yields:
        None
    """
    create_tables()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Session:
    """Provide a transactional database session for a single test.

    Yields:
        Session: A SQLAlchemy sync session connected to the test database.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> TestClient:
    """Provide a Starlette TestClient wrapping the FastAPI app.

    Returns:
        TestClient: Synchronous HTTP test client.
    """
    return TestClient(app)
