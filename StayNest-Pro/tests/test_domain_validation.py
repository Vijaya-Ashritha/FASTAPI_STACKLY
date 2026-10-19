from datetime import date
from pydantic import ValidationError
import pytest
from app.schemas.domain import HotelCreate, RoomCreate, BookingCreate

def test_hotel_requires_name_and_address():
    with pytest.raises(ValidationError): HotelCreate(name="", address="", city="X")
def test_room_price_must_be_positive():
    with pytest.raises(ValidationError): RoomCreate(hotel_id=1,name="A1",room_type="Deluxe",capacity=2,price_per_night=0)
def test_booking_dates_are_parsed():
    b=BookingCreate(room_id=1,check_in=date(2027,1,1),check_out=date(2027,1,3),guests=2)
    assert (b.check_out-b.check_in).days==2
