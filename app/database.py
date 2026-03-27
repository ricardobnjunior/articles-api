"""Database engine, session factory, and base model setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def get_db():
    """Yield a database session and ensure it is closed after use.

    Yields:
        Session: A SQLAlchemy synchronous database session.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all database tables defined in the ORM models.

    This function should be called at application startup to ensure
    all tables exist before handling requests.
    """
    Base.metadata.create_all(bind=engine)
