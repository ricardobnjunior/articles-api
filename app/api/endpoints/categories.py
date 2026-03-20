"""REST API endpoints for category management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryResponse]:
    """List all categories.

    Args:
        db: Database session.

    Returns:
        List of all categories.
    """
    from app.models.category import Category

    return db.query(Category).all()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Create a new category.

    Args:
        category_in: Category creation data.
        db: Database session.

    Returns:
        The created category.

    Raises:
        HTTPException: 400 if category name already exists.
    """
    from app.models.category import Category

    existing = db.query(Category).filter(Category.name == category_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")

    category = Category(name=category_in.name, description=category_in.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Retrieve a single category by ID.

    Args:
        category_id: The category's primary key.
        db: Database session.

    Returns:
        The requested category.

    Raises:
        HTTPException: 404 if category not found.
    """
    from app.models.category import Category

    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Update an existing category.

    Args:
        category_id: The category's primary key.
        category_in: Fields to update.
        db: Database session.

    Returns:
        The updated category.

    Raises:
        HTTPException: 404 if category not found.
    """
    from app.models.category import Category

    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a category.

    Args:
        category_id: The category's primary key.
        db: Database session.

    Raises:
        HTTPException: 404 if category not found.
    """
    from app.models.category import Category

    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
