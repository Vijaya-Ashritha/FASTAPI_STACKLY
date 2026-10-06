
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class PaymentMethod(str, Enum):
    CASH = "Cash"
    CARD = "Card"
    UPI = "UPI"
    BANK_TRANSFER = "Bank Transfer"


class ExpenseStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class CategoryCreate(BaseModel):
    category_id: int
    category_name: str
    description: str


class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    description: str


class ExpenseCreate(BaseModel):
    expense_id: int
    employee_name: str
    category_id: int
    amount: float = Field(gt=0)
    description: str
    expense_date: date
    payment_method: PaymentMethod
    status: ExpenseStatus


class ExpenseResponse(BaseModel):
    expense_id: int
    employee_name: str
    category_id: int
    amount: float
    description: str
    expense_date: date
    payment_method: PaymentMethod
    status: ExpenseStatus
    created_date: datetime


