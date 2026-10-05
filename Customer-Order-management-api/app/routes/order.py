from datetime import date

from fastapi import APIRouter, HTTPException

from app.database import get_connection
from app.schemas import OrderCreate, OrderResponse


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate):
    connection = get_connection()

    try:
        existing_order = connection.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order.order_id,),
        ).fetchone()

        if existing_order:
            raise HTTPException(
                status_code=409,
                detail="Order ID already exists.",
            )

        customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (order.customer_id,),
        ).fetchone()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found.",
            )

        total_amount = order.quantity * order.unit_price
        order_date = date.today().isoformat()

        connection.execute(
            """
            INSERT INTO orders
            (
                order_id,
                customer_id,
                product_name,
                quantity,
                unit_price,
                total_amount,
                order_status,
                order_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order.order_id,
                order.customer_id,
                order.product_name,
                order.quantity,
                order.unit_price,
                total_amount,
                order.order_status.value,
                order_date,
            ),
        )

        connection.commit()

        new_order = connection.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order.order_id,),
        ).fetchone()

        return dict(new_order)

    finally:
        connection.close()


@router.get("/", response_model=list[OrderResponse])
def get_orders():
    connection = get_connection()

    try:
        orders = connection.execute(
            "SELECT * FROM orders ORDER BY order_id"
        ).fetchall()

        return [dict(order) for order in orders]

    finally:
        connection.close()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    connection = get_connection()

    try:
        order = connection.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        return dict(order)

    finally:
        connection.close()


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order: OrderCreate):
    connection = get_connection()

    try:
        existing_order = connection.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()

        if not existing_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        customer = connection.execute(
            "SELECT * FROM customers WHERE customer_id = ?",
            (order.customer_id,),
        ).fetchone()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found.",
            )

        total_amount = order.quantity * order.unit_price

        connection.execute(
            """
            UPDATE orders
            SET customer_id = ?,
                product_name = ?,
                quantity = ?,
                unit_price = ?,
                total_amount = ?,
                order_status = ?
            WHERE order_id = ?
            """,
            (
                order.customer_id,
                order.product_name,
                order.quantity,
                order.unit_price,
                total_amount,
                order.order_status.value,
                order_id,
            ),
        )

        connection.commit()

        updated_order = connection.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()

        return dict(updated_order)

    finally:
        connection.close()


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int):
    connection = get_connection()

    try:
        order = connection.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        connection.execute(
            "DELETE FROM orders WHERE order_id = ?",
            (order_id,),
        )

        connection.commit()

    finally:
        connection.close()