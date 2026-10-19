from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HotelCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=5000)
    address: str = Field(min_length=3, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    country: str = Field(default="", max_length=100)
    amenities: list[str] = Field(default_factory=list)


class HotelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    address: str | None = Field(default=None, min_length=3, max_length=255)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    amenities: list[str] | None = None


class HotelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    description: str
    address: str
    city: str
    country: str
    status: str
    amenities: list[str]


class RoomCreate(BaseModel):
    hotel_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    room_type: str = Field(min_length=2, max_length=50)
    capacity: int = Field(ge=1, le=30)
    price_per_night: float = Field(gt=0, le=10000000)
    amenities: list[str] = Field(default_factory=list)


class RoomUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    room_type: str | None = Field(default=None, min_length=2, max_length=50)
    capacity: int | None = Field(default=None, ge=1, le=30)
    price_per_night: float | None = Field(default=None, gt=0, le=10000000)
    amenities: list[str] | None = None
    is_active: bool | None = None


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    name: str
    room_type: str
    capacity: int
    price_per_night: float
    is_active: bool
    amenities: list[str]


class BookingCreate(BaseModel):
    room_id: int = Field(gt=0)
    check_in: date
    check_out: date
    guests: int = Field(ge=1, le=30)


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    room_id: int
    check_in: datetime
    check_out: datetime
    guests: int
    total_amount: float
    status: str
    payment_status: str


class FeatureRecordCreate(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)


class FeatureRecordOut(BaseModel):
    id: int
    module: str
    owner_id: int
    data: dict[str, Any]
    created_at: datetime

from datetime import date
from pydantic import BaseModel, Field, model_validator


class BookingAmend(BaseModel):
    check_in: date | None = None
    check_out: date | None = None
    guests: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_amendment(self):
        if (
            self.check_in is None
            and self.check_out is None
            and self.guests is None
        ):
            raise ValueError("Provide at least one field to amend")

        if (
            self.check_in is not None
            and self.check_out is not None
            and self.check_out <= self.check_in
        ):
            raise ValueError("check_out must be after check_in")

        return self
