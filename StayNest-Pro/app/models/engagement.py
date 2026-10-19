"""Engagement models.

The original Batch 5 tables are retained for backward compatibility. Batch 9 adds
guest_profiles and reuses the existing reviews, wishlist, and notification tables
instead of redefining those tables with incompatible columns.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import synonym

from app.db.session import Base


class Review(Base):
    __tablename__ = "hotel_reviews"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(120), nullable=False, default="")
    comment = Column(Text, nullable=False, default="")
    is_visible = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Compatibility names used by the Batch 9 endpoints.
    user_id = synonym("customer_id")
    is_published = synonym("is_visible")


HotelReview = Review


class WishlistItem(Base):
    __tablename__ = "hotel_wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("user_id", "hotel_id", name="uq_wishlist_user_hotel"),)


FavoriteHotel = WishlistItem


class Notification(Base):
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_type = Column(String(40), nullable=False, default="GENERAL")
    title = Column(String(160), nullable=False)
    body = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Compatibility names used by the Batch 9 endpoints.
    category = synonym("notification_type")
    message = synonym("body")


UserNotification = Notification


class MessageThread(Base):
    __tablename__ = "message_threads"

    id = Column(Integer, primary_key=True, index=True)
    participant_one_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_two_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(160), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(Base):
    __tablename__ = "thread_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    read_at = Column(DateTime(timezone=True), nullable=True)


class GuestProfile(Base):
    __tablename__ = "guest_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    phone = Column(String(40), nullable=True)
    date_of_birth = Column(String(10), nullable=True)
    preferred_language = Column(String(30), nullable=True)
    special_requests = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
