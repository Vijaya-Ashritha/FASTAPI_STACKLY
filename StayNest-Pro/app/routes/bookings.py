from datetime import datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import Booking, Hotel, Room
from app.models.user import User
from app.schemas.domain import BookingAmend, BookingCreate, BookingOut
router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    body: BookingCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    if user.role != "CUSTOMER":
        raise HTTPException(status_code=403, detail="Only customers can create bookings")
    if body.check_out <= body.check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")

    room = db.get(Room, body.room_id)
    if not room or not room.is_active:
        raise HTTPException(status_code=404, detail="Active room not found")
    hotel = db.get(Hotel, room.hotel_id)
    if not hotel or hotel.status != "APPROVED":
        raise HTTPException(status_code=404, detail="Room is not available for booking")
    if body.guests > room.capacity:
        raise HTTPException(status_code=422, detail="Guest count exceeds room capacity")

    start = datetime.combine(body.check_in, time.min)
    end = datetime.combine(body.check_out, time.min)
    conflict = (
        db.query(Booking)
        .filter(
            Booking.room_id == room.id,
            Booking.status.in_(["PENDING", "CONFIRMED"]),
            Booking.check_in < end,
            Booking.check_out > start,
        )
        .first()
    )
    if conflict:
        raise HTTPException(status_code=409, detail="Room is already booked for these dates")

    nights = (body.check_out - body.check_in).days
    booking = Booking(
        customer_id=user.id,
        room_id=room.id,
        check_in=start,
        check_out=end,
        guests=body.guests,
        total_amount=round(nights * room.price_per_night, 2),
        status="PENDING",
        payment_status="PENDING",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("", response_model=list[BookingOut])
def list_bookings(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    query = db.query(Booking)
    if user.role == "CUSTOMER":
        query = query.filter(Booking.customer_id == user.id)
    elif user.role == "HOTEL_OWNER":
        query = (
            query.join(Room, Booking.room_id == Room.id)
            .join(Hotel, Room.hotel_id == Hotel.id)
            .filter(Hotel.owner_id == user.id)
        )
    elif user.role == "ADMIN":
        pass
    else:
        raise HTTPException(
            status_code=403,
            detail="Hotel staff booking access will be enabled after staff-to-hotel assignment is implemented",
        )
    return query.order_by(Booking.id.desc()).all()


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user.role != "ADMIN" and booking.customer_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot cancel this booking")
    if booking.status not in ("PENDING", "CONFIRMED"):
        raise HTTPException(status_code=409, detail="Booking cannot be cancelled")

    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{booking_id}/confirm", response_model=BookingOut)
def confirm_booking(
    booking_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != "PENDING":
        raise HTTPException(status_code=409, detail="Only pending bookings can be confirmed")

    room = db.get(Room, booking.room_id)
    hotel = db.get(Hotel, room.hotel_id) if room else None
    if user.role != "ADMIN" and (
        user.role != "HOTEL_OWNER" or not hotel or hotel.owner_id != user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the owner of this hotel's rooms or an admin can confirm this booking",
        )

    booking.status = "CONFIRMED"
    db.commit()
    db.refresh(booking)
    return booking
@router.patch("/{booking_id}/amend", response_model=BookingOut)
def amend_booking(
    booking_id: int,
    body: BookingAmend,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    booking = db.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user.role != "ADMIN" and booking.customer_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot amend this booking",
        )

    if booking.status not in {"PENDING", "CONFIRMED"}:
        raise HTTPException(
            status_code=409,
            detail="Only pending or confirmed bookings can be amended",
        )

    if booking.payment_status == "PAID":
        raise HTTPException(
            status_code=409,
            detail="Paid bookings cannot be amended through this endpoint",
        )

    room = db.get(Room, booking.room_id)
    if room is None or not room.is_active:
        raise HTTPException(status_code=409, detail="Booking room is unavailable")

    check_in = body.check_in or booking.check_in.date()
    check_out = body.check_out or booking.check_out.date()
    guests = body.guests if body.guests is not None else booking.guests

    if check_out <= check_in:
        raise HTTPException(
            status_code=422,
            detail="check_out must be after check_in",
        )

    if guests > room.capacity:
        raise HTTPException(
            status_code=422,
            detail="Guest count exceeds room capacity",
        )

    start = datetime.combine(check_in, time.min)
    end = datetime.combine(check_out, time.min)

    conflict = (
        db.query(Booking)
        .filter(
            Booking.room_id == room.id,
            Booking.id != booking.id,
            Booking.status.in_(["PENDING", "CONFIRMED"]),
            Booking.check_in < end,
            Booking.check_out > start,
        )
        .first()
    )

    if conflict:
        raise HTTPException(
            status_code=409,
            detail="Room is already booked for these dates",
        )

    nights = (check_out - check_in).days
    booking.check_in = start
    booking.check_out = end
    booking.guests = guests
    booking.total_amount = round(nights * room.price_per_night, 2)

    db.commit()
    db.refresh(booking)
    return booking

