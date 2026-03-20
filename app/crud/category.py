"""CRUD operations for Category model."""

import re

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _slugify(name: str) -> str:
    """Convert a name string into a URL-friendly slug.

    Args:
        name: The category name to slugify.

    Returns:
        A lowercase, hyphen-separated slug string.
    """
    slug = name.lower().strip()
    # Replace any non-alphanumeric characters (except hyphens) with hyphens
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


def create_category(db: Session, data: CategoryCreate) -> Category:
    """Create a new category with an auto-generated slug.

    Args:
        db: The database session.
        data: The category creation data.

    Returns:
        The newly created Category instance.
    """
    slug = _slugify(data.name)
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
    """Retrieve a category by its ID.

    Args:
        db: The database session.
        category_id: The ID of the category to retrieve.

    Returns:
        The Category instance, or None if not found.
    """
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Category | None:
    """Retrieve a category by its name.

    Args:
        db: The database session.
        name: The name of the category to retrieve.

    Returns:
        The Category instance, or None if not found.
    """
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 50) -> list[Category]:
    """Retrieve a paginated list of categories.

    Args:
        db: The database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of Category instances.
    """
    return db.query(Category).offset(skip).limit(limit).all()


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category | None:
    """Update an existing category.

    Args:
        db: The database session.
        category_id: The ID of the category to update.
        data: The update data.

    Returns:
        The updated Category instance, or None if not found.
    """
    category = get_category(db, category_id)
    if category is None:
        return None

    if data.name is not None:
        category.name = data.name
        category.slug = _slugify(data.name)

    if data.description is not None:
        category.description = data.description

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category by its ID.

    Args:
        db: The database session.
        category_id: The ID of the category to delete.

    Returns:
        True if the category was deleted, False if not found.
    """
    category = get_category(db, category_id)
    if category is None:
        return False

    db.delete(category)
    db.commit()
    return True
