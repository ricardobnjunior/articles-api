"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Provide a database session for dependency injection.

    Yields:
        SQLAlchemy Session instance.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
