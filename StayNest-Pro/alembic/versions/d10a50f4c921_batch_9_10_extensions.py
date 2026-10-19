"""Add StayNest Pro module 41-50 extension tables.

Revision ID: d10a50f4c921
Revises: 5a48aafae60f
Create Date: 2026-10-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "d10a50f4c921"
down_revision: Union[str, Sequence[str], None] = "5a48aafae60f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "guest_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phone", sa.String(40), nullable=True),
        sa.Column("date_of_birth", sa.String(10), nullable=True),
        sa.Column("preferred_language", sa.String(30), nullable=True),
        sa.Column("special_requests", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_guest_profiles_id", "guest_profiles", ["id"])
    op.create_index("ix_guest_profiles_user_id", "guest_profiles", ["user_id"], unique=True)

    op.create_table(
        "subscription_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subscription_id", sa.Integer(), sa.ForeignKey("hotel_subscriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("provider_reference", sa.String(255), nullable=True, unique=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_subscription_payments_id", "subscription_payments", ["id"])
    op.create_index("ix_subscription_payments_subscription_id", "subscription_payments", ["subscription_id"])
    op.create_index("ix_subscription_payments_status", "subscription_payments", ["status"])

    op.create_table(
        "pricing_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("hotel_id", sa.Integer(), sa.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("price_multiplier", sa.Float(), nullable=False),
        sa.Column("fixed_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for col in ("id", "hotel_id", "room_id", "is_active"):
        op.create_index(f"ix_pricing_rules_{col}", "pricing_rules", [col])

    op.create_table(
        "loyalty_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(20), nullable=False),
        sa.Column("idempotency_key", sa.String(160), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for col in ("id", "user_id", "booking_id"):
        op.create_index(f"ix_loyalty_transactions_{col}", "loyalty_transactions", [col])

    op.create_table(
        "hotel_locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("hotel_id", sa.Integer(), sa.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("provider_place_id", sa.String(255), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_hotel_locations_id", "hotel_locations", ["id"])
    op.create_index("ix_hotel_locations_hotel_id", "hotel_locations", ["hotel_id"], unique=True)

    op.create_table(
        "commission_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hotel_id", sa.Integer(), sa.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gross_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("commission_rate", sa.Float(), nullable=False),
        sa.Column("commission_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for col in ("id", "booking_id", "hotel_id", "status"):
        op.create_index(f"ix_commission_records_{col}", "commission_records", [col])

    op.create_table(
        "settlements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("hotel_id", sa.Integer(), sa.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("provider_reference", sa.String(255), nullable=True, unique=True),
        sa.Column("period_start", sa.DateTime(), nullable=False),
        sa.Column("period_end", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for col in ("id", "hotel_id", "status"):
        op.create_index(f"ix_settlements_{col}", "settlements", [col])

    op.create_table(
        "security_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("reviewed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    for col in ("id", "user_id", "event_type", "severity"):
        op.create_index(f"ix_security_events_{col}", "security_events", [col])

    op.create_table(
        "platform_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(120), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_platform_settings_id", "platform_settings", ["id"])
    op.create_index("ix_platform_settings_key", "platform_settings", ["key"], unique=True)


def downgrade() -> None:
    for name, table in [
        ("ix_platform_settings_key", "platform_settings"), ("ix_platform_settings_id", "platform_settings"),
        ("ix_security_events_severity", "security_events"), ("ix_security_events_event_type", "security_events"),
        ("ix_security_events_user_id", "security_events"), ("ix_security_events_id", "security_events"),
        ("ix_settlements_status", "settlements"), ("ix_settlements_hotel_id", "settlements"), ("ix_settlements_id", "settlements"),
        ("ix_commission_records_status", "commission_records"), ("ix_commission_records_hotel_id", "commission_records"),
        ("ix_commission_records_booking_id", "commission_records"), ("ix_commission_records_id", "commission_records"),
        ("ix_hotel_locations_hotel_id", "hotel_locations"), ("ix_hotel_locations_id", "hotel_locations"),
        ("ix_loyalty_transactions_booking_id", "loyalty_transactions"), ("ix_loyalty_transactions_user_id", "loyalty_transactions"),
        ("ix_loyalty_transactions_id", "loyalty_transactions"),
        ("ix_pricing_rules_is_active", "pricing_rules"), ("ix_pricing_rules_room_id", "pricing_rules"),
        ("ix_pricing_rules_hotel_id", "pricing_rules"), ("ix_pricing_rules_id", "pricing_rules"),
        ("ix_subscription_payments_status", "subscription_payments"), ("ix_subscription_payments_subscription_id", "subscription_payments"),
        ("ix_subscription_payments_id", "subscription_payments"),
        ("ix_guest_profiles_user_id", "guest_profiles"), ("ix_guest_profiles_id", "guest_profiles"),
    ]:
        op.drop_index(name, table_name=table)
    for table in ("platform_settings", "security_events", "settlements", "commission_records", "hotel_locations",
                  "loyalty_transactions", "pricing_rules", "subscription_payments", "guest_profiles"):
        op.drop_table(table)
