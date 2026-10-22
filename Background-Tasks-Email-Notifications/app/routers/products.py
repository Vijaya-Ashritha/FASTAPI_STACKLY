
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)
from app.tasks.email_tasks import (
    run_low_stock_email,
    run_inventory_operation_email,
)


router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    product = Product(**product_data.model_dump())

    db.add(product)
    db.commit()
    db.refresh(product)

    # Notify the administrator when a new product is low on stock.
    if product.stock_quantity <= product.reorder_level:
        background_tasks.add_task(
            run_low_stock_email,
            product.name,
            product.stock_quantity,
            product.reorder_level,
        )

    background_tasks.add_task(
        run_inventory_operation_email,
        "Product Created",
        product.name,
        product.stock_quantity,
    )

    return product


@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # Save the old state before applying the update.
    old_stock = product.stock_quantity
    old_reorder_level = product.reorder_level

    updates = product_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    # Send a low-stock alert only when entering the low-stock state.
    was_low_stock = old_stock <= old_reorder_level
    is_low_stock = (
        product.stock_quantity <= product.reorder_level
    )

    if not was_low_stock and is_low_stock:
        background_tasks.add_task(
            run_low_stock_email,
            product.name,
            product.stock_quantity,
            product.reorder_level,
        )

    background_tasks.add_task(
        run_inventory_operation_email,
        "Product Updated",
        product.name,
        product.stock_quantity,
    )

    return product
