from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentRequest(BaseModel):

    card_id: int

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    description: str = Field(
        default="Card payment",
        max_length=255,
    )

    simulate_success: bool = True


class PaymentResponse(BaseModel):

    reference: str

    status: str

    amount: Decimal

    message: str