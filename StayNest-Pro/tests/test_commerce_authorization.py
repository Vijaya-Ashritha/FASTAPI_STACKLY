from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.domain import Booking, Hotel, Room
from app.models.operations import HotelStaffAssignment
from app.models.user import User
from app.routes.commerce import _get_booking


def make_staff_access_case(assignment_exists: bool):
    db = MagicMock()

    booking = MagicMock(spec=Booking)
    booking.id = 100
    booking.customer_id = 10
    booking.room_id = 20

    room = MagicMock(spec=Room)
    room.id = 20
    room.hotel_id = 30

    hotel = MagicMock(spec=Hotel)
    hotel.id = 30
    hotel.owner_id = 40

    staff = MagicMock(spec=User)
    staff.id = 50
    staff.role = "HOTEL_STAFF"

    def get_side_effect(model, object_id):
        if model is Booking and object_id == 100:
            return booking
        if model is Room and object_id == 20:
            return room
        if model is Hotel and object_id == 30:
            return hotel
        return None

    db.get.side_effect = get_side_effect
    db.query.return_value.filter.return_value.first.return_value = (
        (1,) if assignment_exists else None
    )

    return db, booking, staff


def test_unassigned_staff_cannot_access_booking():
    db, booking, staff = make_staff_access_case(assignment_exists=False)

    with pytest.raises(HTTPException) as exc:
        _get_booking(db, booking.id, staff)

    assert exc.value.status_code == 403


def test_assigned_staff_can_access_hotel_booking():
    db, booking, staff = make_staff_access_case(assignment_exists=True)

    result = _get_booking(db, booking.id, staff)

    assert result is booking
    db.query.assert_called_once_with(HotelStaffAssignment.id)


def test_missing_booking_returns_404():
    db = MagicMock()
    db.get.return_value = None

    staff = MagicMock(spec=User)
    staff.id = 50
    staff.role = "HOTEL_STAFF"

    with pytest.raises(HTTPException) as exc:
        _get_booking(db, 999, staff)

    assert exc.value.status_code == 404
