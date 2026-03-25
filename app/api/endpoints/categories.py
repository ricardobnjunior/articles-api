"""API endpoints for category management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.category import (
    create_category,
    delete_category,
    get_categories,
    get_category,
    get_category_by_name,
    update_category,
)
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    data: CategoryCreate, db: Session = Depends(get_db)
) -> CategoryResponse:
    """Create a new category.

    Args:
        data: Category creation payload.
        db: Database session dependency.

    Returns:
        The created category.

    Raises:
        HTTPException: 409 if a category with the same name already exists.
    """
    existing = get_category_by_name(db, data.name)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name '{data.name}' already exists.",
        )
    return create_category(db, data)


@router.get("/", response_model=list[CategoryResponse])
def list_categories_endpoint(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
) -> list[CategoryResponse]:
    """List all categories with optional pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Database session dependency.

    Returns:
        A list of categories.
    """
    return get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(
    category_id: int, db: Session = Depends(get_db)
) -> CategoryResponse:
    """Get a single category by ID.

    Args:
        category_id: The category's primary key.
        db: Database session dependency.

    Returns:
        The requested category.

    Raises:
        HTTPException: 404 if the category does not exist.
    """
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(
    category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)
) -> CategoryResponse:
    """Update an existing category.

    Args:
        category_id: The category's primary key.
        data: Fields to update.
        db: Database session dependency.

    Returns:
        The updated category.

    Raises:
        HTTPException: 404 if the category does not exist.
    """
    category = update_category(db, category_id, data)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(
    category_id: int, db: Session = Depends(get_db)
) -> None:
    """Delete a category by ID.

    Args:
        category_id: The category's primary key.
        db: Database session dependency.

    Raises:
        HTTPException: 404 if the category does not exist.
    """
    deleted = delete_category(db, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found.",
        )
