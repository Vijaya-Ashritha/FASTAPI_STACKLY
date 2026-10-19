"""Additional functional workflows for StayNest Pro.

These endpoints implement useful, database-backed foundations for messaging,
recommendations, dashboards, location data, loyalty, dynamic pricing and settings.
External AI, email, mapping and payment providers still require real credentials.
"""
from datetime import date, datetime, time, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import Booking, Hotel, Room
from app.models.engagement import Message, MessageThread, Notification, WishlistItem
from app.models.platform_extensions import HotelLocation, LoyaltyTransaction, PlatformSetting, PricingRule, SecurityEvent
from app.models.platform_admin import HotelSubscription, SubscriptionPlan
from app.models.user import User

router = APIRouter(prefix="/api/v1", tags=["Completion Workflows"])


def _admin(user: User) -> None:
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin role required")


def _owner_hotel(db: Session, hotel_id: int, user: User) -> Hotel:
    hotel = db.get(Hotel, hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    if user.role != "ADMIN" and not (user.role == "HOTEL_OWNER" and hotel.owner_id == user.id):
        raise HTTPException(status_code=403, detail="You cannot manage this hotel")
    return hotel


class ThreadCreate(BaseModel):
    recipient_user_id: int = Field(gt=0)
    subject: str = Field(min_length=1, max_length=160)
    first_message: str = Field(min_length=1, max_length=5000)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class LocationInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    provider_place_id: str | None = Field(default=None, max_length=255)


class LoyaltyRedeem(BaseModel):
    points: int = Field(gt=0, le=1000000)
    idempotency_key: str = Field(min_length=8, max_length=160)
    description: str = Field(default="Points redeemed", max_length=255)


class SettingInput(BaseModel):
    value: dict
    description: str = Field(default="", max_length=255)


class PricingRuleInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    start_date: datetime
    end_date: datetime
    price_multiplier: float = Field(default=1.0, gt=0, le=10)
    fixed_price: float | None = Field(default=None, gt=0)
    room_id: int | None = Field(default=None, gt=0)


@router.post("/messages/threads", status_code=status.HTTP_201_CREATED)
def create_message_thread(body: ThreadCreate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    recipient = db.get(User, body.recipient_user_id)
    if recipient is None or not recipient.is_active:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if recipient.id == user.id:
        raise HTTPException(status_code=422, detail="You cannot start a conversation with yourself")
    thread = MessageThread(participant_one_id=user.id, participant_two_id=recipient.id, subject=body.subject.strip())
    db.add(thread)
    db.flush()
    message = Message(thread_id=thread.id, sender_id=user.id, content=body.first_message.strip())
    db.add(message)
    db.commit()
    db.refresh(thread)
    return {"id": thread.id, "subject": thread.subject, "participant_one_id": thread.participant_one_id,
            "participant_two_id": thread.participant_two_id, "created_at": thread.created_at,
            "first_message": {"id": message.id, "sender_id": message.sender_id, "content": message.content}}


@router.get("/messages/threads")
def list_message_threads(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], limit: int = Query(50, ge=1, le=100)):
    rows = db.query(MessageThread).filter(or_(MessageThread.participant_one_id == user.id, MessageThread.participant_two_id == user.id)).order_by(MessageThread.updated_at.desc()).limit(limit).all()
    result = []
    for row in rows:
        unread = db.query(func.count(Message.id)).filter(Message.thread_id == row.id, Message.sender_id != user.id, Message.read_at.is_(None)).scalar() or 0
        result.append({"id": row.id, "subject": row.subject, "participant_one_id": row.participant_one_id,
                       "participant_two_id": row.participant_two_id, "updated_at": row.updated_at, "unread_count": unread})
    return result


def _thread_for_user(db: Session, thread_id: int, user_id: int) -> MessageThread:
    row = db.get(MessageThread, thread_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if user_id not in {row.participant_one_id, row.participant_two_id}:
        raise HTTPException(status_code=403, detail="You are not a participant in this conversation")
    return row


@router.get("/messages/threads/{thread_id}/messages")
def list_messages(thread_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], limit: int = Query(100, ge=1, le=200)):
    _thread_for_user(db, thread_id, user.id)
    rows = db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.id.asc()).limit(limit).all()
    for row in rows:
        if row.sender_id != user.id and row.read_at is None:
            row.read_at = datetime.utcnow()
    db.commit()
    return [{"id": row.id, "thread_id": row.thread_id, "sender_id": row.sender_id, "content": row.content,
             "created_at": row.created_at, "read_at": row.read_at} for row in rows]


@router.post("/messages/threads/{thread_id}/messages", status_code=status.HTTP_201_CREATED)
def send_message(thread_id: int, body: MessageCreate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    thread = _thread_for_user(db, thread_id, user.id)
    row = Message(thread_id=thread.id, sender_id=user.id, content=body.content.strip())
    thread.updated_at = datetime.utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "thread_id": row.thread_id, "sender_id": row.sender_id, "content": row.content, "created_at": row.created_at}


@router.put("/hotels/{hotel_id}/location")
def upsert_hotel_location(hotel_id: int, body: LocationInput, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    _owner_hotel(db, hotel_id, user)
    row = db.query(HotelLocation).filter(HotelLocation.hotel_id == hotel_id).first()
    if row is None:
        row = HotelLocation(hotel_id=hotel_id, latitude=body.latitude, longitude=body.longitude, provider_place_id=body.provider_place_id)
        db.add(row)
    else:
        row.latitude, row.longitude, row.provider_place_id = body.latitude, body.longitude, body.provider_place_id
        row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return {"hotel_id": row.hotel_id, "latitude": row.latitude, "longitude": row.longitude,
            "provider_place_id": row.provider_place_id, "updated_at": row.updated_at,
            "provider_note": "Coordinates stored. External map and nearby-attraction lookups require a configured provider."}


@router.get("/locations/nearby-hotels")
def nearby_hotels(latitude: float = Query(ge=-90, le=90), longitude: float = Query(ge=-180, le=180), radius_km: float = Query(25, gt=0, le=500), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Haversine distance is calculated in Python for portability across MySQL versions.
    import math
    rows = db.query(Hotel, HotelLocation).join(HotelLocation, HotelLocation.hotel_id == Hotel.id).filter(Hotel.status == "APPROVED").all()
    matches = []
    for hotel, loc in rows:
        lat1, lat2 = math.radians(latitude), math.radians(loc.latitude)
        dlat, dlon = lat2 - lat1, math.radians(loc.longitude - longitude)
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        distance = 6371 * 2 * math.asin(min(1, math.sqrt(a)))
        if distance <= radius_km:
            matches.append({"hotel_id": hotel.id, "name": hotel.name, "city": hotel.city, "latitude": loc.latitude, "longitude": loc.longitude, "distance_km": round(distance, 2)})
    return sorted(matches, key=lambda item: item["distance_km"])


@router.get("/loyalty/balance")
def loyalty_balance(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    transactions = db.query(LoyaltyTransaction).filter(LoyaltyTransaction.user_id == user.id).all()
    balance = sum((t.points if t.transaction_type.upper() in {"EARN", "CREDIT"} else -abs(t.points)) for t in transactions)
    return {"user_id": user.id, "balance": balance, "transactions": len(transactions)}


@router.post("/loyalty/earn/{booking_id}", status_code=status.HTTP_201_CREATED)
def earn_loyalty_points(booking_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user.role != "ADMIN" and booking.customer_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot earn points for another customer's booking")
    if booking.status not in {"COMPLETED", "CHECKED_OUT"}:
        raise HTTPException(status_code=409, detail="Loyalty points are awarded only after a completed stay")
    key = f"booking-earned-{booking.id}"
    existing = db.query(LoyaltyTransaction).filter(LoyaltyTransaction.idempotency_key == key).first()
    if existing:
        return {"id": existing.id, "booking_id": booking.id, "points": existing.points, "duplicate": True}
    points = max(1, int(float(booking.total_amount) // 10))
    row = LoyaltyTransaction(user_id=booking.customer_id, booking_id=booking.id, points=points, transaction_type="EARN", idempotency_key=key, description="Points earned for completed booking")
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(LoyaltyTransaction).filter(LoyaltyTransaction.idempotency_key == key).first()
        if existing:
            return {"id": existing.id, "booking_id": booking.id, "points": existing.points, "duplicate": True}
        raise
    db.refresh(row)
    return {"id": row.id, "booking_id": booking.id, "points": row.points, "duplicate": False}


@router.post("/loyalty/redeem", status_code=status.HTTP_201_CREATED)
def redeem_loyalty_points(body: LoyaltyRedeem, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    existing = db.query(LoyaltyTransaction).filter(LoyaltyTransaction.idempotency_key == body.idempotency_key).first()
    if existing:
        if existing.user_id != user.id:
            raise HTTPException(status_code=409, detail="Idempotency key already used")
        return {"id": existing.id, "points": existing.points, "duplicate": True}
    rows = db.query(LoyaltyTransaction).filter(LoyaltyTransaction.user_id == user.id).all()
    balance = sum((t.points if t.transaction_type.upper() in {"EARN", "CREDIT"} else -abs(t.points)) for t in rows)
    if body.points > balance:
        raise HTTPException(status_code=409, detail="Insufficient loyalty points")
    row = LoyaltyTransaction(user_id=user.id, points=body.points, transaction_type="REDEEM", idempotency_key=body.idempotency_key, description=body.description)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "points_redeemed": row.points, "remaining_balance": balance - row.points, "duplicate": False}


@router.get("/recommendations")
def recommend_hotels(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], city: str | None = None, max_price: float | None = Query(default=None, gt=0), limit: int = Query(default=10, ge=1, le=50)):
    query = db.query(Hotel).filter(Hotel.status == "APPROVED")
    if city:
        query = query.filter(func.lower(Hotel.city) == city.strip().lower())
    hotels = query.order_by(Hotel.name.asc()).limit(200).all()
    results = []
    for hotel in hotels:
        rooms = db.query(Room).filter(Room.hotel_id == hotel.id, Room.is_active.is_(True))
        if max_price is not None:
            rooms = rooms.filter(Room.price_per_night <= max_price)
        room_count = rooms.count()
        if max_price is not None and room_count == 0:
            continue
        favorite = db.query(WishlistItem.id).filter(WishlistItem.user_id == user.id, WishlistItem.hotel_id == hotel.id).first() is not None
        results.append({"hotel_id": hotel.id, "name": hotel.name, "city": hotel.city, "description": hotel.description,
                        "active_room_count": room_count, "is_favorite": favorite,
                        "reason": "Matches requested city/budget and approved listing status"})
    return {"strategy": "rule_based", "external_ai_configured": False, "items": results[:limit],
            "note": "This is a transparent rule-based baseline, not an external AI recommendation model."}


@router.post("/support/answer")
def support_answer(question: str = Query(min_length=3, max_length=1000), user: User = Depends(get_current_user)):
    q = question.lower()
    if any(word in q for word in ("cancel", "cancellation", "refund")):
        answer = "Open your booking in the booking APIs and submit a cancellation or refund request. Eligibility depends on the booking status and applicable hotel policy."
    elif any(word in q for word in ("payment", "stripe", "card")):
        answer = "Payments use the configured Stripe integration. A payment is confirmed only after the signed provider webhook is processed; never send card numbers or CVV to this API."
    elif any(word in q for word in ("check in", "check-in", "check out", "check-out")):
        answer = "Check-in and check-out are available for an eligible booking through the booking operations endpoints, subject to role and booking-status checks."
    elif any(word in q for word in ("booking", "reservation", "room")):
        answer = "Use hotel search and availability first, then create a booking with valid dates and guest count. The API validates that check-out is after check-in."
    else:
        answer = "I can provide basic guidance for bookings, payments, cancellations, refunds, and check-in/out. For account-specific help, use an authorized support workflow."
    return {"answer": answer, "source": "configured_faq_rules", "external_ai_configured": False, "user_id": user.id}


@router.get("/dashboards/customer")
def customer_dashboard(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    bookings = db.query(Booking).filter(Booking.customer_id == user.id)
    upcoming = bookings.filter(Booking.check_in >= datetime.utcnow(), Booking.status.notin_(["CANCELLED", "COMPLETED"])).count()
    total = bookings.count()
    unread = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)).count()
    favorites = db.query(WishlistItem).filter(WishlistItem.user_id == user.id).count()
    return {"user_id": user.id, "total_bookings": total, "upcoming_bookings": upcoming, "favorite_hotels": favorites, "unread_notifications": unread}


@router.get("/hotels/{hotel_id}/dashboard")
def owner_dashboard(hotel_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    hotel = _owner_hotel(db, hotel_id, user)
    room_ids = [r.id for r in db.query(Room.id).filter(Room.hotel_id == hotel.id).all()]
    bookings = db.query(Booking).filter(Booking.room_id.in_(room_ids)) if room_ids else db.query(Booking).filter(Booking.id == -1)
    total_bookings = bookings.count()
    active_bookings = bookings.filter(Booking.status.in_(["PENDING", "CONFIRMED", "CHECKED_IN"])).count()
    revenue = db.query(func.coalesce(func.sum(Booking.total_amount), 0)).filter(Booking.room_id.in_(room_ids), Booking.payment_status == "PAID", Booking.status.notin_(["CANCELLED"])).scalar() if room_ids else 0
    return {"hotel_id": hotel.id, "hotel_name": hotel.name, "room_count": len(room_ids), "total_bookings": total_bookings, "active_bookings": active_bookings, "paid_booking_revenue": float(revenue or 0), "status": hotel.status}


@router.get("/analytics/revenue")
def revenue_analytics(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], start_date: date, end_date: date, hotel_id: int | None = None):
    if end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")
    q = db.query(Booking).join(Room, Booking.room_id == Room.id).join(Hotel, Room.hotel_id == Hotel.id).filter(
        Booking.payment_status == "PAID", Booking.status != "CANCELLED",
        Booking.created_at >= datetime.combine(start_date, time.min),
        Booking.created_at < datetime.combine(end_date + timedelta(days=1), time.min))
    if user.role == "HOTEL_OWNER":
        q = q.filter(Hotel.owner_id == user.id)
    elif user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Owner or admin role required")
    if hotel_id is not None:
        if user.role == "HOTEL_OWNER": _owner_hotel(db, hotel_id, user)
        q = q.filter(Hotel.id == hotel_id)
    rows = q.all()
    return {"start_date": start_date, "end_date": end_date, "paid_booking_count": len(rows), "gross_paid_booking_revenue": round(sum(float(b.total_amount) for b in rows), 2), "note": "Gross paid booking amount; refunds, taxes and commissions are not deducted in this summary."}


@router.get("/analytics/occupancy")
def occupancy_analytics(hotel_id: int, start_date: date, end_date: date, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    hotel = _owner_hotel(db, hotel_id, user)
    if end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")
    room_count = db.query(Room).filter(Room.hotel_id == hotel.id, Room.is_active.is_(True)).count()
    days = (end_date - start_date).days + 1
    bookings = db.query(Booking).join(Room, Booking.room_id == Room.id).filter(
        Room.hotel_id == hotel.id, Booking.status.notin_(["CANCELLED"]),
        Booking.check_in < datetime.combine(end_date + timedelta(days=1), time.min),
        Booking.check_out > datetime.combine(start_date, time.min)).all()
    occupied_nights = 0
    for booking in bookings:
        first = max(start_date, booking.check_in.date())
        last = min(end_date + timedelta(days=1), booking.check_out.date())
        occupied_nights += max(0, (last - first).days)
    capacity = room_count * days
    return {"hotel_id": hotel.id, "start_date": start_date, "end_date": end_date, "active_rooms": room_count,
            "occupied_room_nights": occupied_nights, "available_room_nights": max(0, capacity - occupied_nights),
            "occupancy_rate_percent": round(occupied_nights / capacity * 100, 2) if capacity else 0.0}


@router.post("/hotels/{hotel_id}/pricing-rules", status_code=status.HTTP_201_CREATED)
def create_pricing_rule(hotel_id: int, body: PricingRuleInput, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    _owner_hotel(db, hotel_id, user)
    if body.end_date <= body.start_date:
        raise HTTPException(status_code=422, detail="end_date must be later than start_date")
    if body.room_id is not None:
        room = db.get(Room, body.room_id)
        if room is None or room.hotel_id != hotel_id:
            raise HTTPException(status_code=422, detail="room_id must belong to the selected hotel")
    overlap = db.query(PricingRule).filter(PricingRule.hotel_id == hotel_id, PricingRule.is_active.is_(True),
        PricingRule.start_date < body.end_date, PricingRule.end_date > body.start_date,
        or_(PricingRule.room_id == body.room_id, PricingRule.room_id.is_(None), body.room_id is None)).first()
    if overlap:
        raise HTTPException(status_code=409, detail="An active pricing rule overlaps this date range")
    row = PricingRule(hotel_id=hotel_id, room_id=body.room_id, name=body.name.strip(), start_date=body.start_date,
                      end_date=body.end_date, price_multiplier=body.price_multiplier, fixed_price=body.fixed_price, is_active=True)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "hotel_id": row.hotel_id, "room_id": row.room_id, "name": row.name,
            "start_date": row.start_date, "end_date": row.end_date, "price_multiplier": row.price_multiplier,
            "fixed_price": float(row.fixed_price) if row.fixed_price is not None else None, "is_active": row.is_active}


@router.get("/rooms/{room_id}/price-quote")
def room_price_quote(room_id: int, check_in: date, check_out: date, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    room = db.get(Room, room_id)
    if room is None or not room.is_active:
        raise HTTPException(status_code=404, detail="Active room not found")
    if check_out <= check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")
    nights = (check_out - check_in).days
    base = float(room.price_per_night)
    start_dt = datetime.combine(check_in, time.min)
    end_dt = datetime.combine(check_out, time.min)
    rules = db.query(PricingRule).filter(PricingRule.hotel_id == room.hotel_id, PricingRule.is_active.is_(True),
        PricingRule.start_date < end_dt, PricingRule.end_date > start_dt,
        or_(PricingRule.room_id == room.id, PricingRule.room_id.is_(None))).order_by(PricingRule.room_id.desc()).all()
    nightly = []
    for offset in range(nights):
        current = check_in + timedelta(days=offset)
        active = [r for r in rules if r.start_date.date() <= current < r.end_date.date()]
        price = base
        if active:
            rule = active[0]
            price = float(rule.fixed_price) if rule.fixed_price is not None else base * float(rule.price_multiplier)
        nightly.append({"date": current, "price": round(price, 2)})
    return {"room_id": room.id, "check_in": check_in, "check_out": check_out, "nights": nights,
            "nightly_prices": nightly, "total_before_taxes_and_discounts": round(sum(x["price"] for x in nightly), 2),
            "note": "This is a quote endpoint. Booking creation must use the same pricing logic to lock the final amount."}


@router.get("/admin/settings")
def list_platform_settings(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    _admin(user)
    return [{"id": x.id, "key": x.key, "value": x.value, "description": x.description, "updated_at": x.updated_at} for x in db.query(PlatformSetting).order_by(PlatformSetting.key).all()]


@router.put("/admin/settings/{key}")
def upsert_platform_setting(key: str, body: SettingInput, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    _admin(user)
    if not key.strip() or len(key) > 120:
        raise HTTPException(status_code=422, detail="key must contain 1 to 120 characters")
    row = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
    if row is None:
        row = PlatformSetting(key=key, value=body.value, description=body.description, updated_by=user.id)
        db.add(row)
    else:
        row.value, row.description, row.updated_by, row.updated_at = body.value, body.description, user.id, datetime.utcnow()
    db.commit()
    db.refresh(row)
    return {"id": row.id, "key": row.key, "value": row.value, "description": row.description, "updated_at": row.updated_at}


@router.get("/admin/security-events")
def list_security_events(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], reviewed: bool | None = None, limit: int = Query(100, ge=1, le=500)):
    _admin(user)
    q = db.query(SecurityEvent)
    if reviewed is not None:
        q = q.filter(SecurityEvent.reviewed.is_(reviewed))
    return [{"id": e.id, "user_id": e.user_id, "event_type": e.event_type, "severity": e.severity,
             "ip_address": e.ip_address, "details": e.details, "reviewed": e.reviewed, "created_at": e.created_at}
            for e in q.order_by(SecurityEvent.created_at.desc()).limit(limit).all()]


@router.patch("/admin/security-events/{event_id}/review")
def review_security_event(event_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    _admin(user)
    event = db.get(SecurityEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Security event not found")
    event.reviewed = True
    db.commit()
    return {"id": event.id, "reviewed": event.reviewed}


class SubscriptionInput(BaseModel):
    plan_id: int = Field(gt=0)
    billing_months: int = Field(default=1, ge=1, le=36)


@router.post("/hotels/{hotel_id}/subscription", status_code=status.HTTP_201_CREATED)
def create_or_change_hotel_subscription(hotel_id: int, body: SubscriptionInput, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    _owner_hotel(db, hotel_id, user)
    plan = db.get(SubscriptionPlan, body.plan_id)
    if plan is None or not plan.is_active:
        raise HTTPException(status_code=404, detail="Active subscription plan not found")
    now = datetime.utcnow()
    current = db.query(HotelSubscription).filter(HotelSubscription.hotel_id == hotel_id, HotelSubscription.status == "ACTIVE").first()
    if current:
        current.status = "UPGRADED" if float(plan.price) >= float(db.get(SubscriptionPlan, current.plan_id).price) else "DOWNGRADED"
        current.expires_at = now
    subscription = HotelSubscription(hotel_id=hotel_id, plan_id=plan.id, status="ACTIVE", starts_at=now,
                                     expires_at=now + timedelta(days=30 * body.billing_months))
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return {"id": subscription.id, "hotel_id": subscription.hotel_id, "plan_id": subscription.plan_id,
            "plan_name": plan.name, "status": subscription.status, "starts_at": subscription.starts_at,
            "expires_at": subscription.expires_at,
            "billing_note": "Subscription record created only; Stripe recurring billing and webhook reconciliation are not configured by this endpoint."}


@router.get("/hotels/{hotel_id}/subscription")
def get_hotel_subscription(hotel_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    _owner_hotel(db, hotel_id, user)
    row = db.query(HotelSubscription).filter(HotelSubscription.hotel_id == hotel_id).order_by(HotelSubscription.created_at.desc()).first()
    if row is None:
        raise HTTPException(status_code=404, detail="No subscription found for this hotel")
    plan = db.get(SubscriptionPlan, row.plan_id)
    return {"id": row.id, "hotel_id": row.hotel_id, "plan_id": row.plan_id, "plan_name": plan.name if plan else None,
            "status": row.status, "starts_at": row.starts_at, "expires_at": row.expires_at}


@router.get("/admin/analytics/customers")
def customer_analytics(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], start_date: date | None = None, end_date: date | None = None):
    _admin(user)
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")
    q = db.query(Booking).filter(Booking.status != "CANCELLED")
    if start_date:
        q = q.filter(Booking.created_at >= datetime.combine(start_date, time.min))
    if end_date:
        q = q.filter(Booking.created_at < datetime.combine(end_date + timedelta(days=1), time.min))
    rows = q.all()
    by_customer: dict[int, list[Booking]] = {}
    for booking in rows:
        by_customer.setdefault(booking.customer_id, []).append(booking)
    spend_rows = [b for b in rows if b.payment_status == "PAID"]
    return {"start_date": start_date, "end_date": end_date, "customers_with_bookings": len(by_customer),
            "repeat_customers": sum(1 for items in by_customer.values() if len(items) > 1),
            "paid_booking_count": len(spend_rows), "paid_booking_value": round(sum(float(b.total_amount) for b in spend_rows), 2),
            "average_paid_booking_value": round(sum(float(b.total_amount) for b in spend_rows) / len(spend_rows), 2) if spend_rows else 0.0,
            "note": "Metrics are booking-derived approximations; customer retention cohorts and service revenue are not included."}


@router.get("/admin/analytics/business-intelligence")
def business_intelligence(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], limit: int = Query(default=10, ge=1, le=50)):
    _admin(user)
    hotels = db.query(Hotel).all()
    ranking = []
    for hotel in hotels:
        room_ids = [row[0] for row in db.query(Room.id).filter(Room.hotel_id == hotel.id).all()]
        if not room_ids:
            revenue = 0.0
            booking_count = 0
        else:
            paid = db.query(Booking).filter(Booking.room_id.in_(room_ids), Booking.payment_status == "PAID", Booking.status != "CANCELLED").all()
            revenue = round(sum(float(b.total_amount) for b in paid), 2)
            booking_count = len(paid)
        ranking.append({"hotel_id": hotel.id, "hotel_name": hotel.name, "city": hotel.city, "paid_booking_revenue": revenue, "paid_booking_count": booking_count})
    ranking.sort(key=lambda item: item["paid_booking_revenue"], reverse=True)
    return {"top_hotels_by_paid_booking_revenue": ranking[:limit], "hotel_count": len(hotels),
            "note": "Baseline ranking based on paid bookings; excludes service revenue, refunds, taxes, settlements and date-trend analysis."}
