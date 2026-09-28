from fastapi import APIRouter, HTTPException, Query

from app.database import get_connection
from app.schemas import ProductCreate, ProductResponse


router = APIRouter(prefix="/products", tags=["Products"])


# CREATE PRODUCT
@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate):
    connection = get_connection()

    existing_product = connection.execute(
        "SELECT * FROM products WHERE product_id = ?",
        (product.product_id,),
    ).fetchone()

    if existing_product:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Product ID already exists",
        )

    connection.execute(
        """
        INSERT INTO products
        (product_id, product_name, category, price, quantity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            product.product_id,
            product.product_name,
            product.category,
            product.price,
            product.quantity,
        ),
    )

    connection.commit()
    connection.close()

    return product


# GET ALL PRODUCTS / SEARCH BY CATEGORY
@router.get("/", response_model=list[ProductResponse])
def get_products(category: str | None = Query(default=None)):
    connection = get_connection()

    if category:
        products = connection.execute(
            "SELECT * FROM products WHERE category = ?",
            (category,),
        ).fetchall()
    else:
        products = connection.execute(
            "SELECT * FROM products"
        ).fetchall()

    connection.close()

    return [dict(product) for product in products]


# GET PRODUCT BY ID
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    connection = get_connection()

    product = connection.execute(
        "SELECT * FROM products WHERE product_id = ?",
        (product_id,),
    ).fetchone()

    connection.close()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return dict(product)


# UPDATE PRODUCT
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate):
    connection = get_connection()

    existing_product = connection.execute(
        "SELECT * FROM products WHERE product_id = ?",
        (product_id,),
    ).fetchone()

    if not existing_product:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    connection.execute(
        """
        UPDATE products
        SET product_name = ?,
            category = ?,
            price = ?,
            quantity = ?
        WHERE product_id = ?
        """,
        (
            product.product_name,
            product.category,
            product.price,
            product.quantity,
            product_id,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "product_id": product_id,
        "product_name": product.product_name,
        "category": product.category,
        "price": product.price,
        "quantity": product.quantity,
    }


# DELETE PRODUCT
@router.delete("/{product_id}")
def delete_product(product_id: int):
    connection = get_connection()

    existing_product = connection.execute(
        "SELECT * FROM products WHERE product_id = ?",
        (product_id,),
    ).fetchone()

    if not existing_product:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    connection.execute(
        "DELETE FROM products WHERE product_id = ?",
        (product_id,),
    )

    connection.commit()
    connection.close()

    return {"message": "Product deleted successfully"}