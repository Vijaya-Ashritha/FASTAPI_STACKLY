import pytest
from pydantic import ValidationError

from app.schemas.operations import (
    HotelServiceCreate,
    HousekeepingTaskCreate,
    RoomServiceOrderCreate,
    RoomServiceOrderItemCreate,
    StaffAssignmentCreate,
)


def test_staff_assignment_requires_positive_ids():
    with pytest.raises(ValidationError):
        StaffAssignmentCreate(hotel_id=0, user_id=2)


def test_housekeeping_task_requires_positive_room_id():
    with pytest.raises(ValidationError):
        HousekeepingTaskCreate(hotel_id=1, room_id=0)


def test_hotel_service_rejects_negative_price():
    with pytest.raises(ValidationError):
        HotelServiceCreate(
            hotel_id=1,
            name="Laundry",
            price=-1,
        )


def test_hotel_service_accepts_zero_price():
    service = HotelServiceCreate(
        hotel_id=1,
        name="Free Wi-Fi",
        price=0,
    )
    assert service.price == 0


def test_room_service_item_requires_positive_quantity():
    with pytest.raises(ValidationError):
        RoomServiceOrderItemCreate(service_id=1, quantity=0)


def test_room_service_order_requires_at_least_one_item():
    with pytest.raises(ValidationError):
        RoomServiceOrderCreate(booking_id=1, items=[])


def test_room_service_order_rejects_too_many_items():
    with pytest.raises(ValidationError):
        RoomServiceOrderCreate(
            booking_id=1,
            items=[
                RoomServiceOrderItemCreate(service_id=i, quantity=1)
                for i in range(1, 52)
            ],
        )
