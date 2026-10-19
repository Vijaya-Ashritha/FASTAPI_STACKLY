

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StaffAssignmentCreate(BaseModel):
    hotel_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    assignment_role: str = Field(default="GENERAL", min_length=2, max_length=40)


class StaffAssignmentUpdate(BaseModel):
    assignment_role: str | None = Field(default=None, min_length=2, max_length=40)
    is_active: bool | None = None


class StaffAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    user_id: int
    assignment_role: str
    is_active: bool
    created_by: int
    created_at: datetime


class HousekeepingTaskCreate(BaseModel):
    hotel_id: int = Field(gt=0)
    room_id: int = Field(gt=0)
    assigned_staff_id: int | None = Field(default=None, gt=0)
    task_type: str = Field(default="CLEANING", min_length=2, max_length=40)
    notes: str = Field(default="", max_length=3000)
    scheduled_at: datetime | None = None


class HousekeepingTaskUpdate(BaseModel):
    assigned_staff_id: int | None = Field(default=None, gt=0)
    status: str | None = None
    notes: str | None = Field(default=None, max_length=3000)
    scheduled_at: datetime | None = None


class HousekeepingTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    room_id: int
    assigned_staff_id: int | None
    created_by: int
    task_type: str
    status: str
    notes: str
    scheduled_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class HotelServiceCreate(BaseModel):
    hotel_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=3000)
    price: float = Field(ge=0, le=10000000)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    is_available: bool = True


class HotelServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=3000)
    price: float | None = Field(default=None, ge=0, le=10000000)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    is_available: bool | None = None


class HotelServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    name: str
    description: str
    price: float
    currency: str
    is_available: bool
    created_at: datetime


class RoomServiceOrderItemCreate(BaseModel):
    service_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=100)


class RoomServiceOrderCreate(BaseModel):
    booking_id: int = Field(gt=0)
    items: list[RoomServiceOrderItemCreate] = Field(min_length=1, max_length=50)
    notes: str = Field(default="", max_length=2000)


class RoomServiceOrderStatusUpdate(BaseModel):
    status: str


class RoomServiceOrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    service_id: int
    service_name: str
    quantity: int
    unit_price: float
    line_total: float


class RoomServiceOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    hotel_id: int
    room_id: int
    customer_id: int
    status: str
    total_amount: float
    notes: str
    created_at: datetime
    updated_at: datetime
    items: list[RoomServiceOrderItemOut] = []
