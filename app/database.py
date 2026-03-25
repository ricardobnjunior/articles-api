"""Database engine, session factory, and base model for SQLAlchemy (sync)."""

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
    """Declarative base class for all ORM models."""


def get_db():
    """Yield a SQLAlchemy database session and ensure it is closed afterwards.

    Yields:
        Session: An active SQLAlchemy sync session.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined in the ORM metadata.

    This function is called at application startup to ensure the schema
    exists before any requests are handled.
    """
    Base.metadata.create_all(bind=engine)
