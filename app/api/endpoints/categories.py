"""API endpoints for categories."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category.

    Args:
        data: Category creation payload.
        db: Database session.

    Returns:
        The created category.
    """
    category = Category(name=data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """List all categories.

    Args:
        db: Database session.

    Returns:
        List of all categories.
    """
    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a single category by ID.

    Args:
        category_id: The category's primary key.
        db: Database session.

    Returns:
        The category if found.

    Raises:
        HTTPException: 404 if not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
