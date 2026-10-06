from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.database import get_connection
from app.schemas import ExpenseCreate, ExpenseResponse


router = APIRouter(prefix="/expenses", tags=["Expenses"])


# CREATE EXPENSE
@router.post("/", response_model=ExpenseResponse, status_code=201)
def create_expense(expense: ExpenseCreate):
    connection = get_connection()

    try:
        existing_expense = connection.execute(
            "SELECT * FROM expenses WHERE expense_id = ?",
            (expense.expense_id,),
        ).fetchone()

        if existing_expense:
            raise HTTPException(
                status_code=400,
                detail="Expense ID already exists",
            )

        category = connection.execute(
            "SELECT * FROM categories WHERE category_id = ?",
            (expense.category_id,),
        ).fetchone()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        created_date = datetime.now()

        connection.execute(
            """
            INSERT INTO expenses
            (
                expense_id,
                employee_name,
                category_id,
                amount,
                description,
                expense_date,
                payment_method,
                status,
                created_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                expense.expense_id,
                expense.employee_name,
                expense.category_id,
                expense.amount,
                expense.description,
                expense.expense_date.isoformat(),
                expense.payment_method.value,
                expense.status.value,
                created_date.isoformat(),
            ),
        )

        connection.commit()

        return {
            "expense_id": expense.expense_id,
            "employee_name": expense.employee_name,
            "category_id": expense.category_id,
            "amount": expense.amount,
            "description": expense.description,
            "expense_date": expense.expense_date,
            "payment_method": expense.payment_method,
            "status": expense.status,
            "created_date": created_date,
        }

    finally:
        connection.close()


# GET ALL EXPENSES + FILTERS
@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(
    category_id: int | None = None,
    status: str | None = None,
    payment_method: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    connection = get_connection()

    try:
        query = "SELECT * FROM expenses WHERE 1=1"
        parameters = []

        if category_id is not None:
            query += " AND category_id = ?"
            parameters.append(category_id)

        if status is not None:
            query += " AND status = ?"
            parameters.append(status)

        if payment_method is not None:
            query += " AND payment_method = ?"
            parameters.append(payment_method)

        if start_date is not None:
            query += " AND expense_date >= ?"
            parameters.append(start_date)

        if end_date is not None:
            query += " AND expense_date <= ?"
            parameters.append(end_date)

        expenses = connection.execute(
            query,
            parameters,
        ).fetchall()

        return [dict(expense) for expense in expenses]

    finally:
        connection.close()


# GET EXPENSE BY ID
@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int):
    connection = get_connection()

    try:
        expense = connection.execute(
            "SELECT * FROM expenses WHERE expense_id = ?",
            (expense_id,),
        ).fetchone()

        if not expense:
            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        return dict(expense)

    finally:
        connection.close()


# UPDATE EXPENSE
@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense: ExpenseCreate,
):
    connection = get_connection()

    try:
        existing_expense = connection.execute(
            "SELECT * FROM expenses WHERE expense_id = ?",
            (expense_id,),
        ).fetchone()

        if not existing_expense:
            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        category = connection.execute(
            "SELECT * FROM categories WHERE category_id = ?",
            (expense.category_id,),
        ).fetchone()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        connection.execute(
            """
            UPDATE expenses
            SET employee_name = ?,
                category_id = ?,
                amount = ?,
                description = ?,
                expense_date = ?,
                payment_method = ?,
                status = ?
            WHERE expense_id = ?
            """,
            (
                expense.employee_name,
                expense.category_id,
                expense.amount,
                expense.description,
                expense.expense_date.isoformat(),
                expense.payment_method.value,
                expense.status.value,
                expense_id,
            ),
        )

        connection.commit()

        updated_expense = connection.execute(
            "SELECT * FROM expenses WHERE expense_id = ?",
            (expense_id,),
        ).fetchone()

        return dict(updated_expense)

    finally:
        connection.close()


# DELETE EXPENSE
@router.delete("/{expense_id}")
def delete_expense(expense_id: int):
    connection = get_connection()

    try:
        expense = connection.execute(
            "SELECT * FROM expenses WHERE expense_id = ?",
            (expense_id,),
        ).fetchone()

        if not expense:
            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        connection.execute(
            "DELETE FROM expenses WHERE expense_id = ?",
            (expense_id,),
        )

        connection.commit()

        return {"message": "Expense deleted successfully"}

    finally:
        connection.close()


# TOTAL EXPENSES
@router.get("/total")
def get_total_expenses():
    connection = get_connection()

    try:
        result = connection.execute(
            "SELECT SUM(amount) AS total_expenses FROM expenses"
        ).fetchone()

        total = result["total_expenses"]

        if total is None:
            total = 0

        return {
            "total_expenses": total
        }
                                                                
    finally:
        connection.close() 