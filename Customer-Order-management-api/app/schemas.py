from datetime import date
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class OrderStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class CustomerCreate(BaseModel):
    customer_id: int
    customer_name: str = Field(min_length=1)
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    city: str | None = None


class CustomerResponse(BaseModel):
    customer_id: int
    customer_name: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    created_date: date


class OrderCreate(BaseModel):
    order_id: int
    customer_id: int
    product_name: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    order_status: OrderStatus = OrderStatus.PENDING


class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    order_status: OrderStatus
    order_date: date