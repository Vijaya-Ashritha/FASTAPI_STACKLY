from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


def utc_now():
    return datetime.now(timezone.utc)


class Guest(Base):
    __tablename__ = "booking_guests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="", nullable=False)
    special_requests: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Payment(Base):
    __tablename__ = "booking_payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Invoice(Base):
    __tablename__ = "booking_invoices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ISSUED", nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Coupon(Base):
    __tablename__ = "coupons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    discount_type: Mapped[str] = mapped_column(String(10), nullable=False)  # PERCENT or FIXED
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    max_redemptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    redemption_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class CouponRedemption(Base):
    __tablename__ = "coupon_redemptions"
    __table_args__ = (UniqueConstraint("booking_id", name="uq_coupon_redemption_booking"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id"), index=True, nullable=False)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class RefundRequest(Base):
    __tablename__ = "booking_refund_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), index=True, nullable=False)
    payment_id: Mapped[int] = mapped_column(ForeignKey("booking_payments.id"), index=True, nullable=False)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="REQUESTED", index=True, nullable=False)
    stripe_refund_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class StripeWebhookEvent(Base):
    __tablename__ = "stripe_webhook_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
