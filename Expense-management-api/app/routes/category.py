from fastapi import APIRouter, HTTPException

from app.database import get_connection
from app.schemas import CategoryCreate, CategoryResponse


router = APIRouter(prefix="/categories", tags=["Categories"])


# CREATE CATEGORY
@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate):
    connection = get_connection()

    try:
        existing_id = connection.execute(
            "SELECT * FROM categories WHERE category_id = ?",
            (category.category_id,),
        ).fetchone()

        if existing_id:
            raise HTTPException(
                status_code=400,
                detail="Category ID already exists",
            )

        existing_name = connection.execute(
            "SELECT * FROM categories WHERE category_name = ?",
            (category.category_name,),
        ).fetchone()

        if existing_name:
            raise HTTPException(
                status_code=400,
                detail="Category name already exists",
            )

        connection.execute(
            """
            INSERT INTO categories
            (category_id, category_name, description)
            VALUES (?, ?, ?)
            """,
            (
                category.category_id,
                category.category_name,
                category.description,
            ),
        )

        connection.commit()

        return category

    finally:
        connection.close()


# GET ALL CATEGORIES
@router.get("/", response_model=list[CategoryResponse])
def get_categories():
    connection = get_connection()

    try:
        categories = connection.execute(
            "SELECT * FROM categories"
        ).fetchall()

        return [dict(category) for category in categories]

    finally:
        connection.close()


# GET CATEGORY BY ID
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int):
    connection = get_connection()

    try:
        category = connection.execute(
            "SELECT * FROM categories WHERE category_id = ?",
            (category_id,),
        ).fetchone()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        return dict(category)

    finally:
        connection.close()


# UPDATE CATEGORY
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryCreate):
    connection = get_connection()

    try:
        existing_category = connection.execute(
            "SELECT * FROM categories WHERE category_id = ?",
            (category_id,),
        ).fetchone()

        if not existing_category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        duplicate_name = connection.execute(
            """
            SELECT * FROM categories
            WHERE category_name = ? AND category_id != ?
            """,
            (category.category_name, category_id),
        ).fetchone()

        if duplicate_name:
            raise HTTPException(
                status_code=400,
                detail="Category name already exists",
            )

        connection.execute(
            """
            UPDATE categories
            SET category_name = ?, description = ?
            WHERE category_id = ?
            """,
            (
                category.category_name,
                category.description,
                category_id,
            ),
        )

        connection.commit()

        updated_category = connection.execute(
            "SELECT * FROM categories WHERE category_id = ?",
            (category_id,),
        ).fetchone()

        return dict(updated_category)

    finally:
        connection.close()


# DELETE CATEGORY
@router.delete("/{category_id}")
def delete_category(category_id: int):
    connection = get_connection()

    try:
        category = connection.execute(
            "SELECT * FROM categories WHERE category_id = ?",
            (category_id,),
        ).fetchone()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        expense = connection.execute(
            "SELECT * FROM expenses WHERE category_id = ?",
            (category_id,),
        ).fetchone()

        if expense:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete category because expenses exist for this category",
            )

        connection.execute(
            "DELETE FROM categories WHERE category_id = ?",
            (category_id,),
        )

        connection.commit()

        return {"message": "Category deleted successfully"}

    finally:
        connection.close()