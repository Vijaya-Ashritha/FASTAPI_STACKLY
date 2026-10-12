
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product
from app.schemas import (
    InventoryValueResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    category = db.get(Category, data.category_id)

    if category is None:
        raise HTTPException(
            status_code=400,
            detail="Category does not exist",
        )

    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@router.get("/inventory-value", response_model=InventoryValueResponse)
def get_inventory_value(db: Session = Depends(get_db)):
    total = (
        db.query(
            func.coalesce(
                func.sum(Product.price * Product.quantity),
                0.0,
            )
        )
        .scalar()
    )

    return {"total_inventory_value": round(float(total), 2)}


@router.get("", response_model=list[ProductResponse])
def get_products(
    category_id: int | None = Query(default=None, gt=0),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    search: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code=422,
                detail="min_price cannot be greater than max_price",
            )

    if search is not None:
        query = query.filter(
            Product.product_name.ilike(f"%{search.strip()}%")
        )

    return query.order_by(Product.product_id).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    changes = data.model_dump(exclude_unset=True)

    for field in ("product_name", "category_id", "price", "quantity"):
        if field in changes and changes[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

    if "category_id" in changes:
        category = db.get(Category, changes["category_id"])

        if category is None:
            raise HTTPException(
                status_code=400,
                detail="Category does not exist",
            )

    for field, value in changes.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
