import os
import sys
import uuid

from pathlib import Path
import pymysql

BASE_DIR = Path(
    __file__
).resolve().parent.parent


sys.path.insert(
    0,
    str(BASE_DIR),
)

pymysql.install_as_MySQLdb()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "credit_system.settings",
)


import django

django.setup()


from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException

from cards.models import Card

from transactions.models import Transaction

from .auth import get_current_user_id

from .schemas import (
    PaymentRequest,
    PaymentResponse,
)


app = FastAPI(
    title="Credit Card Payment Service",
    description=(
        "FastAPI service for simulated "
        "credit/debit card payments."
    ),
    version="1.0.0",
)


@app.get("/")
def home():

    return {
        "message": (
            "Payment service is running"
        )
    }


@app.post(
    "/payments",
    response_model=PaymentResponse,
)
def make_payment(
    data: PaymentRequest,
    user_id: int = Depends(
        get_current_user_id
    ),
):

    card = (
        Card.objects
        .filter(
            id=data.card_id,
            user_id=user_id,
        )
        .first()
    )

    if not card:

        raise HTTPException(
            status_code=404,
            detail="Card not found.",
        )


    reference = (
        f"PAY-"
        f"{uuid.uuid4().hex[:12].upper()}"
    )


    transaction = (
        Transaction.objects.create(
            user_id=user_id,
            card=card,
            amount=data.amount,
            status="PENDING",
            reference=reference,
            description=data.description,
        )
    )


    if data.simulate_success:

        transaction.status = "SUCCESS"

        message = "Payment successful."

    else:

        transaction.status = "FAILED"

        message = (
            "Payment failed in simulation."
        )


    transaction.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )


    return PaymentResponse(
        reference=transaction.reference,
        status=transaction.status,
        amount=transaction.amount,
        message=message,
    )