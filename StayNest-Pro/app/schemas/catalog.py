from pydantic import BaseModel, ConfigDict, Field

class RoomTypeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    capacity: int = Field(default=2, ge=1, le=30)
    base_price: float = Field(default=0, ge=0)

class RoomTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    capacity: int | None = Field(default=None, ge=1, le=30)
    base_price: float | None = Field(default=None, ge=0)
    is_active: bool | None = None

class RoomTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel_id: int
    name: str
    description: str | None
    capacity: int
    base_price: float
    is_active: bool

class HotelAmenityCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    category: str | None = Field(default=None, max_length=60)

class HotelAmenityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    category: str | None = Field(default=None, max_length=60)

class HotelAmenityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel_id: int
    name: str
    description: str | None
    category: str | None

class AvailabilityOut(BaseModel):
    room_id: int
    check_in: str
    check_out: str
    available: bool
