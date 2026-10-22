from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.product import Product
from app.schemas.file import ProductImageAssociation
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
)
from app.services.file_service import get_owned_file_or_404


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=201,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    product = Product(
        name=payload.name.strip(),
        owner_id=user_id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@router.get("", response_model=ProductListResponse)
def list_products(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    statement = (
        select(Product)
        .options(joinedload(Product.image))
        .where(Product.owner_id == user_id)
        .order_by(Product.id.desc())
    )

    items = list(
        db.scalars(statement).unique().all()
    )

    return {
        "items": items,
        "total": len(items),
    }


@router.put(
    "/{product_id}/image",
    response_model=ProductResponse,
)
def associate_product_image(
    product_id: int,
    payload: ProductImageAssociation,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    product = db.scalar(
        select(Product).where(
            Product.id == product_id,
            Product.owner_id == user_id,
        )
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    file_record = get_owned_file_or_404(
        db,
        payload.image_id,
        user_id,
    )

    if file_record.file_kind != "product_image":
        raise HTTPException(
            status_code=422,
            detail="Only product_image files can be associated",
        )

    product.image_id = file_record.id
    db.commit()
    db.refresh(product)

    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    product = db.scalar(
        select(Product).where(
            Product.id == product_id,
            Product.owner_id == user_id,
        )
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    product.image_id = None
    db.delete(product)
    db.commit()

    return None
