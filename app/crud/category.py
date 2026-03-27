"""CRUD operations for Category resources."""

import re
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _generate_slug(name: str) -> str:
    """Generate a URL-safe slug from a category name.

    Converts the name to lowercase, replaces spaces and non-alphanumeric
    characters with hyphens, and strips leading/trailing hyphens.

    Args:
        name: The category name to convert.

    Returns:
        A URL-safe slug string.
    """
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def create_category(db: Session, data: CategoryCreate) -> Optional[Category]:
    """Create a new category with an auto-generated slug.

    Args:
        db: SQLAlchemy database session.
        data: Category creation data.

    Returns:
        The newly created Category instance, or None if name already exists.
    """
    slug = _generate_slug(data.name)
    category = Category(
        name=data.name,
        slug=slug,
        description=data.description,
    )
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        return None


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Retrieve a single category by its primary key.

    Args:
        db: SQLAlchemy database session.
        category_id: The category's primary key.

    Returns:
        The Category instance if found, otherwise None.
    """
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 50) -> List[Category]:
    """Retrieve a paginated list of categories.

    Args:
        db: SQLAlchemy database session.
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.

    Returns:
        A list of Category instances.
    """
    return db.query(Category).offset(skip).limit(limit).all()


def update_category(
    db: Session, category_id: int, data: CategoryUpdate
) -> Optional[Category]:
    """Update an existing category.

    Re-generates the slug if the name is updated.

    Args:
        db: SQLAlchemy database session.
        category_id: The category's primary key.
        data: Fields to update.

    Returns:
        The updated Category instance, or None if not found.
    """
    category = get_category(db, category_id)
    if category is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] is not None:
        update_data["slug"] = _generate_slug(update_data["name"])

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category by its primary key.

    Args:
        db: SQLAlchemy database session.
        category_id: The category's primary key.

    Returns:
        True if the category was deleted, False if not found.
    """
    category = get_category(db, category_id)
    if category is None:
        return False
    db.delete(category)
    db.commit()
    return True
