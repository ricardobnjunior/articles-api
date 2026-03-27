"""Test configuration and fixtures for the test suite."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create all tables before each test and drop them after.

    This fixture runs automatically for every test, ensuring a clean
    database state for each test function.
    """
    # Import models so they register with Base.metadata
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(setup_test_db) -> Session:
    """Yield a transactional database session for direct DB access in tests.

    Args:
        setup_test_db: Ensures tables exist before yielding session.

    Yields:
        Session: A SQLAlchemy synchronous database session.
    """
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(setup_test_db) -> TestClient:
    """Return a TestClient that uses the in-memory test database.

    Overrides the FastAPI app's `get_db` dependency to use the test
    engine, ensuring full isolation from production data.

    Args:
        setup_test_db: Ensures tables exist before the client is used.

    Returns:
        TestClient: A synchronous HTTP test client.
    """

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
