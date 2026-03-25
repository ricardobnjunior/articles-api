"""CRUD operations for Category model."""

import re

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a category name.

    Args:
        name: The human-readable category name.

    Returns:
        A lowercase, hyphen-separated slug string.
    """
    slug = name.lower()
    slug = slug.strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def create_category(db: Session, data: CategoryCreate) -> Category:
    """Create a new category.

    Args:
        db: SQLAlchemy database session.
        data: Category creation data.

    Returns:
        The newly created Category instance.
    """
    slug = _generate_slug(data.name)
    category = Category(
        name=data.name,
        slug=slug,
        description=data.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> Category | None:
    """Retrieve a single category by ID.

    Args:
        db: SQLAlchemy database session.
        category_id: Primary key of the category.

    Returns:
        The Category instance, or None if not found.
    """
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Category | None:
    """Retrieve a single category by name.

    Args:
        db: SQLAlchemy database session.
        name: The exact category name to look up.

    Returns:
        The Category instance, or None if not found.
    """
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 50) -> list[Category]:
    """Retrieve a list of categories with pagination.

    Args:
        db: SQLAlchemy database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of Category instances.
    """
    return db.query(Category).offset(skip).limit(limit).all()


def update_category(
    db: Session, category_id: int, data: CategoryUpdate
) -> Category | None:
    """Update an existing category.

    Args:
        db: SQLAlchemy database session.
        category_id: Primary key of the category to update.
        data: Fields to update.

    Returns:
        The updated Category instance, or None if not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return None

    if data.name is not None:
        category.name = data.name
        category.slug = _generate_slug(data.name)
    if data.description is not None:
        category.description = data.description

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category by ID.

    Args:
        db: SQLAlchemy database session.
        category_id: Primary key of the category to delete.

    Returns:
        True if the category was deleted, False if not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return False

    db.delete(category)
    db.commit()
    return True
