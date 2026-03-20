"""Database engine, session factory, and base model for SQLAlchemy (sync)."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


def _make_engine():
    """Create the SQLAlchemy engine from settings."""
    settings = get_settings()
    kwargs = {}
    if "sqlite" in settings.database_url:
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(settings.database_url, **kwargs)


engine = _make_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for use as a FastAPI dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables defined by ORM models."""
    import app.models  # noqa: F401 — ensure models are registered

    Base.metadata.create_all(bind=engine)
