from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class GuestCreate(BaseModel):
    booking_id: int = Field(gt=0)
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(default="", max_length=40)
    special_requests: str = Field(default="", max_length=2000)


class GuestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    booking_id: int
    customer_id: int
    full_name: str
    email: EmailStr
    phone: str
    special_requests: str
    created_at: datetime


class PaymentIntentCreate(BaseModel):
    booking_id: int = Field(gt=0)
    currency: str = Field(default="usd", min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        value = value.lower()
        if not value.isalpha():
            raise ValueError("Currency must contain three letters")
        return value


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    booking_id: int
    customer_id: int
    amount: float
    currency: str
    status: str
    stripe_payment_intent_id: str | None
    created_at: datetime


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    invoice_number: str
    booking_id: int
    customer_id: int
    amount: float
    currency: str
    status: str
    issued_at: datetime


class CouponCreate(BaseModel):
    code: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    discount_type: str
    discount_value: float = Field(gt=0)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    max_redemptions: int | None = Field(default=None, gt=0)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, value: str) -> str:
        value = value.upper()
        if value not in {"PERCENT", "FIXED"}:
            raise ValueError("discount_type must be PERCENT or FIXED")
        return value

    @field_validator("discount_value")
    @classmethod
    def validate_discount_value(cls, value: float, info):
        if info.data.get("discount_type") == "PERCENT" and value > 100:
            raise ValueError("Percentage discount cannot exceed 100")
        return value


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    discount_type: str
    discount_value: float
    active: bool
    valid_from: datetime | None
    valid_until: datetime | None
    max_redemptions: int | None
    redemption_count: int
    created_by: int
    created_at: datetime


class CouponApply(BaseModel):
    code: str = Field(min_length=3, max_length=40)


class CouponApplyOut(BaseModel):
    booking_id: int
    coupon_code: str
    original_amount: float
    discount_amount: float
    final_amount: float


class RefundCreate(BaseModel):
    booking_id: int = Field(gt=0)
    payment_id: int = Field(gt=0)
    amount: float | None = Field(default=None, gt=0)
    reason: str = Field(default="", max_length=2000)


class RefundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    booking_id: int
    payment_id: int
    requested_by: int
    amount: float
    reason: str
    status: str
    stripe_refund_id: str | None
    created_at: datetime
    processed_at: datetime | None
