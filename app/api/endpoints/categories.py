"""REST API endpoints for categories."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> List[CategoryResponse]:
    """List all categories.

    Args:
        db: Database session.

    Returns:
        List of all categories.
    """
    return db.query(Category).all()


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Create a new category.

    Args:
        category_data: Validated category creation data.
        db: Database session.

    Returns:
        The newly created category.
    """
    # Check for duplicate name
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    db_category = Category(name=category_data.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryResponse:
    """Get a single category by ID.

    Args:
        category_id: Primary key of the category.
        db: Database session.

    Returns:
        The category if found.

    Raises:
        HTTPException: 404 if category not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a category by ID.

    Args:
        category_id: Primary key of the category.
        db: Database session.

    Raises:
        HTTPException: 404 if category not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
