"""Database engine and session configuration."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./articles.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


def get_db():
    """Provide a database session as a FastAPI dependency.

    Yields:
        SQLAlchemy Session instance.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
