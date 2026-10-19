from datetime import datetime, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.commerce import (
    Coupon, CouponRedemption, Guest, Invoice, Payment, RefundRequest, StripeWebhookEvent,
)
from app.models.domain import Booking, Hotel, Room
from app.models.operations import HotelStaffAssignment
from app.models.user import User
from app.schemas.commerce import (
    CouponApply, CouponApplyOut, CouponCreate, CouponOut, GuestCreate, GuestOut,
    InvoiceOut, PaymentIntentCreate, PaymentOut, RefundCreate, RefundOut,
)

router = APIRouter(tags=["Batch 4 - Booking, Payments and Revenue"])


def _get_booking(db: Session, booking_id: int, user: User) -> Booking:
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user.role == "ADMIN" or booking.customer_id == user.id:
        return booking

    room = db.get(Room, booking.room_id)
    hotel = db.get(Hotel, room.hotel_id) if room else None

    if hotel and user.role == "HOTEL_OWNER" and hotel.owner_id == user.id:
        return booking

    if hotel and user.role == "HOTEL_STAFF":
        assignment = (
            db.query(HotelStaffAssignment.id)
            .filter(
                HotelStaffAssignment.hotel_id == hotel.id,
                HotelStaffAssignment.user_id == user.id,
                HotelStaffAssignment.is_active.is_(True),
            )
            .first()
        )
        if assignment is not None:
            return booking

    raise HTTPException(status_code=403, detail="You cannot access this booking")


def _stripe():
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe is not configured. Set STRIPE_SECRET_KEY in .env")
    try:
        import stripe
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Stripe SDK missing; install with python -m pip install stripe") from exc
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def _invoice_for_booking(db: Session, booking: Booking, currency: str) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.booking_id == booking.id).first()
    if invoice:
        return invoice
    invoice = Invoice(
        invoice_number=f"SN-{booking.id}-{uuid4().hex[:10].upper()}",
        booking_id=booking.id,
        customer_id=booking.customer_id,
        amount=round(float(booking.total_amount), 2),
        currency=currency.lower(),
        status="ISSUED",
    )
    db.add(invoice)
    db.flush()
    return invoice


@router.post("/api/v1/guests", response_model=GuestOut, status_code=201)
def create_guest(body: GuestCreate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    booking = _get_booking(db, body.booking_id, user)
    if user.role not in {"CUSTOMER", "ADMIN"} or (user.role == "CUSTOMER" and booking.customer_id != user.id):
        raise HTTPException(status_code=403, detail="Only the booking customer or an admin can add guest details")
    guest = Guest(
        booking_id=booking.id, customer_id=booking.customer_id,
        full_name=body.full_name.strip(), email=str(body.email).lower(),
        phone=body.phone.strip(), special_requests=body.special_requests.strip(),
    )
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest


@router.get("/api/v1/guests", response_model=list[GuestOut])
def list_guests(booking_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    _get_booking(db, booking_id, user)
    return db.query(Guest).filter(Guest.booking_id == booking_id).order_by(Guest.id.asc()).all()


@router.post("/api/v1/payments/intent", status_code=201)
def create_payment_intent(body: PaymentIntentCreate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    booking = _get_booking(db, body.booking_id, user)
    if booking.customer_id != user.id and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only the booking customer can pay for this booking")
    if booking.status in {"CANCELLED", "COMPLETED"}:
        raise HTTPException(status_code=409, detail="This booking cannot be paid")
    if db.query(Payment).filter(Payment.booking_id == booking.id, Payment.status == "SUCCEEDED").first():
        raise HTTPException(status_code=409, detail="This booking is already paid")
    stripe = _stripe()
    payment = Payment(
        booking_id=booking.id, customer_id=booking.customer_id,
        amount=round(float(booking.total_amount), 2), currency=body.currency.lower(),
        status="PENDING", idempotency_key=f"staynest-payment-{uuid4().hex}",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(round(payment.amount * 100)), currency=payment.currency,
            metadata={"booking_id": str(booking.id), "payment_id": str(payment.id)},
            idempotency_key=payment.idempotency_key,
        )
        payment.stripe_payment_intent_id = intent.id
        db.commit()
        db.refresh(payment)
        return {
            "payment": PaymentOut.model_validate(payment),
            "client_secret": intent.client_secret,
            "message": "Confirm payment with Stripe.js or an official Stripe client; never send raw card details to this API.",
        }
    except Exception as exc:
        payment.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=502, detail="Stripe could not create a payment intent") from exc


@router.post("/api/v1/payments/webhook")
async def stripe_webhook(request: Request, stripe_signature: Annotated[str | None, Header(alias="Stripe-Signature")] = None, db: Session = Depends(get_db)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Set STRIPE_WEBHOOK_SECRET in .env before enabling webhooks")
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")
    stripe = _stripe()
    try:
        event = stripe.Webhook.construct_event(await request.body(), stripe_signature, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature or payload") from exc
    if db.query(StripeWebhookEvent).filter(StripeWebhookEvent.event_id == event["id"]).first():
        return {"received": True, "duplicate": True}
    event_type = event["type"]
    obj = event["data"]["object"]
    payment = db.query(Payment).filter(Payment.stripe_payment_intent_id == obj.get("id")).first()
    db.add(StripeWebhookEvent(event_id=event["id"], event_type=event_type))
    if payment and event_type == "payment_intent.succeeded":
        payment.status = "SUCCEEDED"
        booking = db.get(Booking, payment.booking_id)
        if booking:
            booking.payment_status = "PAID"
            if booking.status == "PENDING":
                booking.status = "CONFIRMED"
            _invoice_for_booking(db, booking, payment.currency)
    elif payment and event_type in {"payment_intent.payment_failed", "payment_intent.canceled"}:
        payment.status = "FAILED" if event_type.endswith("failed") else "CANCELLED"
        booking = db.get(Booking, payment.booking_id)
        if booking and booking.payment_status != "PAID":
            booking.payment_status = "FAILED"
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"received": True, "duplicate": True}
    return {"received": True, "duplicate": False}


@router.get("/api/v1/payments", response_model=list[PaymentOut])
def list_payments(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], booking_id: int | None = None):
    query = db.query(Payment)
    if user.role != "ADMIN":
        query = query.filter(Payment.customer_id == user.id)
    if booking_id is not None:
        _get_booking(db, booking_id, user)
        query = query.filter(Payment.booking_id == booking_id)
    return query.order_by(Payment.id.desc()).limit(200).all()


@router.get("/api/v1/invoices", response_model=list[InvoiceOut])
def list_invoices(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    query = db.query(Invoice)
    if user.role != "ADMIN":
        query = query.filter(Invoice.customer_id == user.id)
    return query.order_by(Invoice.id.desc()).limit(200).all()


@router.get("/api/v1/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    _get_booking(db, invoice.booking_id, user)
    return invoice


@router.post("/api/v1/coupons", response_model=CouponOut, status_code=201)
def create_coupon(body: CouponCreate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only an admin can create coupons")
    if body.valid_from and body.valid_until and body.valid_until <= body.valid_from:
        raise HTTPException(status_code=422, detail="valid_until must be later than valid_from")
    coupon = Coupon(
        code=body.code, discount_type=body.discount_type, discount_value=body.discount_value,
        valid_from=body.valid_from, valid_until=body.valid_until,
        max_redemptions=body.max_redemptions, created_by=user.id,
    )
    db.add(coupon)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Coupon code already exists") from exc
    db.refresh(coupon)
    return coupon


@router.get("/api/v1/coupons", response_model=list[CouponOut])
def list_coupons(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    query = db.query(Coupon)
    if user.role != "ADMIN":
        query = query.filter(Coupon.active.is_(True))
    return query.order_by(Coupon.id.desc()).limit(200).all()


@router.post("/api/v1/coupons/apply", response_model=CouponApplyOut)
def apply_coupon(body: CouponApply, booking_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    booking = _get_booking(db, booking_id, user)
    if booking.customer_id != user.id and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only the booking customer can apply a coupon")
    if booking.payment_status == "PAID":
        raise HTTPException(status_code=409, detail="A coupon cannot be applied after payment")
    if db.query(CouponRedemption).filter(CouponRedemption.booking_id == booking.id).first():
        raise HTTPException(status_code=409, detail="A coupon has already been applied to this booking")
    coupon = db.query(Coupon).filter(Coupon.code == body.code.strip().upper(), Coupon.active.is_(True)).first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="Active coupon not found")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start = coupon.valid_from.replace(tzinfo=None) if coupon.valid_from and coupon.valid_from.tzinfo else coupon.valid_from
    end = coupon.valid_until.replace(tzinfo=None) if coupon.valid_until and coupon.valid_until.tzinfo else coupon.valid_until
    if start and now < start:
        raise HTTPException(status_code=409, detail="Coupon is not active yet")
    if end and now > end:
        raise HTTPException(status_code=409, detail="Coupon has expired")
    if coupon.max_redemptions is not None and coupon.redemption_count >= coupon.max_redemptions:
        raise HTTPException(status_code=409, detail="Coupon redemption limit reached")
    original = round(float(booking.total_amount), 2)
    discount = original * coupon.discount_value / 100 if coupon.discount_type == "PERCENT" else coupon.discount_value
    discount = round(min(original, discount), 2)
    booking.total_amount = round(max(0, original - discount), 2)
    coupon.redemption_count += 1
    db.add(CouponRedemption(coupon_id=coupon.id, booking_id=booking.id, customer_id=booking.customer_id, discount_amount=discount))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="A coupon has already been applied to this booking") from exc
    return CouponApplyOut(booking_id=booking.id, coupon_code=coupon.code, original_amount=original, discount_amount=discount, final_amount=round(float(booking.total_amount), 2))


@router.post("/api/v1/refunds", response_model=RefundOut, status_code=201)
def request_refund(body: RefundCreate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    booking = _get_booking(db, body.booking_id, user)
    if booking.customer_id != user.id and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only the booking customer can request a refund")
    payment = db.get(Payment, body.payment_id)
    if payment is None or payment.booking_id != booking.id or payment.status != "SUCCEEDED":
        raise HTTPException(status_code=409, detail="A successful payment for this booking is required")
    amount = round(float(body.amount if body.amount is not None else payment.amount), 2)
    if amount <= 0 or amount > payment.amount:
        raise HTTPException(status_code=422, detail="Refund amount must be positive and no greater than the payment")
    existing = db.query(RefundRequest).filter(RefundRequest.payment_id == payment.id, RefundRequest.status.in_(["REQUESTED", "PROCESSING", "SUCCEEDED"])).first()
    if existing:
        raise HTTPException(status_code=409, detail="A refund request already exists for this payment")
    refund = RefundRequest(booking_id=booking.id, payment_id=payment.id, requested_by=user.id, amount=amount, reason=body.reason.strip(), status="REQUESTED")
    db.add(refund)
    db.commit()
    db.refresh(refund)
    return refund


@router.get("/api/v1/refunds", response_model=list[RefundOut])
def list_refunds(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    query = db.query(RefundRequest)
    if user.role != "ADMIN":
        query = query.filter(RefundRequest.requested_by == user.id)
    return query.order_by(RefundRequest.id.desc()).limit(200).all()


@router.post("/api/v1/refunds/{refund_id}/process", response_model=RefundOut)
def process_refund(refund_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    refund = db.get(RefundRequest, refund_id)
    if refund is None:
        raise HTTPException(status_code=404, detail="Refund request not found")
    booking = _get_booking(db, refund.booking_id, user)
    if user.role != "ADMIN":
        room = db.get(Room, booking.room_id)
        hotel = db.get(Hotel, room.hotel_id) if room else None
        if user.role != "HOTEL_OWNER" or hotel is None or hotel.owner_id != user.id:
            raise HTTPException(status_code=403, detail="Only an admin or owning hotel owner can process refunds")
    if refund.status != "REQUESTED":
        raise HTTPException(status_code=409, detail="Only requested refunds can be processed")
    payment = db.get(Payment, refund.payment_id)
    if payment is None or not payment.stripe_payment_intent_id:
        raise HTTPException(status_code=409, detail="Stripe payment intent is missing")
    stripe = _stripe()
    try:
        result = stripe.Refund.create(payment_intent=payment.stripe_payment_intent_id, amount=int(round(refund.amount * 100)), idempotency_key=f"staynest-refund-{refund.id}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Stripe could not process the refund") from exc
    refund.stripe_refund_id = result.id
    refund.status = "SUCCEEDED" if result.status == "succeeded" else "PROCESSING"
    refund.processed_at = datetime.now(timezone.utc)
    if refund.status == "SUCCEEDED" and round(refund.amount, 2) >= round(payment.amount, 2):
        payment.status = "REFUNDED"
        booking.payment_status = "REFUNDED"
    db.commit()
    db.refresh(refund)
    return refund


@router.post("/api/v1/bookings/{booking_id}/check-in")
def check_in_booking(booking_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    booking = _get_booking(db, booking_id, user)
    if user.role not in {"ADMIN", "HOTEL_OWNER", "HOTEL_STAFF"}:
        raise HTTPException(status_code=403, detail="Only hotel staff, hotel owners, or admins can check in guests")
    if booking.status != "CONFIRMED" or booking.payment_status != "PAID":
        raise HTTPException(status_code=409, detail="Booking must be confirmed and paid before check-in")
    booking.status = "CHECKED_IN"
    booking.checked_in_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(booking)
    return {
        "booking_id": booking.id,
        "status": booking.status,
        "checked_in_at": booking.checked_in_at,
    }


@router.post("/api/v1/bookings/{booking_id}/check-out")
def check_out_booking(booking_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    booking = _get_booking(db, booking_id, user)
    if user.role not in {"ADMIN", "HOTEL_OWNER", "HOTEL_STAFF"}:
        raise HTTPException(status_code=403, detail="Only hotel staff, hotel owners, or admins can check out guests")
    if booking.status != "CHECKED_IN":
        raise HTTPException(status_code=409, detail="Only checked-in bookings can be checked out")
    booking.status = "COMPLETED"
    booking.checked_out_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(booking)
    return {
        "booking_id": booking.id,
        "status": booking.status,
        "checked_in_at": booking.checked_in_at,
        "checked_out_at": booking.checked_out_at,
    }
