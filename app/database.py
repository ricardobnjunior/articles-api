"""Database engine, session factory, and base model configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""


def get_engine():
    """Create SQLAlchemy engine from current settings.

    Returns:
        SQLAlchemy engine instance.
    """
    settings = get_settings()
    return create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
        if "sqlite" in settings.database_url
        else {},
    )


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency that provides a database session.

    Yields:
        SQLAlchemy Session instance, closed after request completes.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
