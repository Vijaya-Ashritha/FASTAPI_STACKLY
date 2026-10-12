
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductResponse,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Category)
        .filter(Category.category_name == data.category_name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Category name already exists",
        )

    category = Category(**data.model_dump())
    db.add(category)

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category name already exists",
        )

    return category


@router.get("", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.category_id).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    changes = data.model_dump(exclude_unset=True)

    if "category_name" in changes and changes["category_name"] is None:
        raise HTTPException(status_code=422, detail="Category name cannot be null")

    if "category_name" in changes:
        existing = (
            db.query(Category)
            .filter(
                Category.category_name == changes["category_name"],
                Category.category_id != category_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Category name already exists",
            )

    for field, value in changes.items():
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category name already exists",
        )

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    product = (
        db.query(Product)
        .filter(Product.category_id == category_id)
        .first()
    )

    if product:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a category that contains products",
        )

    db.delete(category)
    db.commit()


@router.get("/{category_id}/products", response_model=list[ProductResponse])
def get_category_products(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return (
        db.query(Product)
        .filter(Product.category_id == category_id)
        .order_by(Product.product_id)
        .all()
    )
