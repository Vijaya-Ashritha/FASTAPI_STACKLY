from datetime import date

from fastapi import APIRouter, HTTPException

from app.database import get_connection
from app.schemas import CustomerCreate, CustomerResponse


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate):
    connection = get_connection()

    try:
        existing_customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (customer.customer_id,),
        ).fetchone()

        if existing_customer:
            raise HTTPException(
                status_code=409,
                detail="Customer ID already exists.",
            )

        existing_email = connection.execute(
            "SELECT * FROM customers WHERE email = ?",
            (customer.email,),
        ).fetchone()

        if existing_email:
            raise HTTPException(
                status_code=409,
                detail="Customer email already exists.",
            )

        created_date = date.today().isoformat()

        connection.execute(
            """
            INSERT INTO customers
            (
                customer_id,
                customer_name,
                email,
                phone,
                address,
                city,
                created_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer.customer_id,
                customer.customer_name,
                customer.email,
                customer.phone,
                customer.address,
                customer.city,
                created_date,
            ),
        )

        connection.commit()

        new_customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (customer.customer_id,),
        ).fetchone()

        return dict(new_customer)

    finally:
        connection.close()


@router.get("/", response_model=list[CustomerResponse])
def get_customers():
    connection = get_connection()

    try:
        customers = connection.execute(
            "SELECT * FROM customers ORDER BY customer_id"
        ).fetchall()

        return [dict(customer) for customer in customers]

    finally:
        connection.close()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int):
    connection = get_connection()

    try:
        customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found.",
            )

        return dict(customer)

    finally:
        connection.close()


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer: CustomerCreate):
    connection = get_connection()

    try:
        existing_customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()

        if not existing_customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found.",
            )

        email_customer = connection.execute(
            """
            SELECT * FROM customers
            WHERE email = ? AND customer_id != ?
            """,
            (customer.email, customer_id),
        ).fetchone()

        if email_customer:
            raise HTTPException(
                status_code=409,
                detail="Customer email already exists.",
            )

        connection.execute(
            """
            UPDATE customers
            SET customer_name = ?,
                email = ?,
                phone = ?,
                address = ?,
                city = ?
            WHERE customer_id = ?
            """,
            (
                customer.customer_name,
                customer.email,
                customer.phone,
                customer.address,
                customer.city,
                customer_id,
            ),
        )

        connection.commit()

        updated_customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()

        return dict(updated_customer)

    finally:
        connection.close()


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int):
    connection = get_connection()

    try:
        customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found.",
            )

        existing_orders = connection.execute(
            "SELECT * FROM orders WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()

        if existing_orders:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete customer because orders exist.",
            )

        connection.execute(
            "DELETE FROM customers WHERE customer_id = ?",
            (customer_id,),
        )

        connection.commit()

    finally:
        connection.close()