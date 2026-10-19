from app.db.session import Base
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.models.domain import Hotel, Room, Booking, FeatureRecord
from app.models.gallery import GalleryImage
from app.models.catalog import HotelAmenity, RoomType
from app.models.commerce import Guest, Payment, Invoice, Coupon, CouponRedemption, RefundRequest, StripeWebhookEvent
from app.models.engagement import Review, WishlistItem, Notification, MessageThread, Message
from app.models.operations import HotelStaffAssignment, HousekeepingTask, HotelService, RoomServiceOrder, RoomServiceOrderItem

__all__ = [
    "Base", "User", "RefreshToken", "Hotel", "Room", "Booking", "FeatureRecord",
    "GalleryImage", "HotelAmenity", "RoomType", "Guest", "Payment", "Invoice",
    "Coupon", "CouponRedemption", "RefundRequest", "StripeWebhookEvent",
    "Review", "WishlistItem", "Notification", "MessageThread", "Message",
    "HotelStaffAssignment", "HousekeepingTask", "HotelService",
    "RoomServiceOrder", "RoomServiceOrderItem",
]

# Batch 8: admin, verification, audit, and subscription models
from app.models.platform_admin import AuditLog, HotelSubscription, HotelVerificationDocument, SubscriptionPlan


# Batch 9-10: subscription payments, pricing, loyalty, locations, finance and security
from app.models.platform_extensions import (
    CommissionRecord, HotelLocation, LoyaltyTransaction, PlatformSetting,
    PricingRule, SecurityEvent, Settlement, SubscriptionPayment,
)
