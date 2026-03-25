"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# SQLAlchemy engine for SQLite with connection arguments for thread safety
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Session factory bound to the engine
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    __abstract__ = True


def get_db():
    """Dependency generator for database sessions.

    Yields:
        Session: SQLAlchemy database session.

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in Base.metadata."""
    Base.metadata.create_all(bind=engine)
