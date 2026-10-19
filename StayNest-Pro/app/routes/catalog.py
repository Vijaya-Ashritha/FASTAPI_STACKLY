from datetime import date, datetime, time
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import Booking, Hotel, Room
from app.models.catalog import HotelAmenity, RoomType
from app.models.user import User
from app.schemas.catalog import (AvailabilityOut, HotelAmenityCreate, HotelAmenityOut,
    HotelAmenityUpdate, RoomTypeCreate, RoomTypeOut, RoomTypeUpdate)

router = APIRouter(prefix="/api/v1", tags=["Room Types, Amenities & Availability"])

def _hotel_or_404(db: Session, hotel_id: int) -> Hotel:
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

def _can_manage_hotel(user: User, hotel: Hotel) -> bool:
    return user.role == "ADMIN" or hotel.owner_id == user.id

@router.post("/hotels/{hotel_id}/room-types", response_model=RoomTypeOut, status_code=status.HTTP_201_CREATED)
def create_room_type(hotel_id: int, payload: RoomTypeCreate, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    hotel = _hotel_or_404(db, hotel_id)
    if not _can_manage_hotel(user, hotel):
        raise HTTPException(status_code=403, detail="You cannot manage this hotel")
    if db.query(RoomType).filter(RoomType.hotel_id == hotel_id, RoomType.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Room type name already exists")
    item = RoomType(hotel_id=hotel_id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/hotels/{hotel_id}/room-types", response_model=list[RoomTypeOut])
def list_room_types(hotel_id: int, db: Session = Depends(get_db)):
    hotel = _hotel_or_404(db, hotel_id)
    if hotel.status != "APPROVED":
        raise HTTPException(status_code=404, detail="Hotel not found")
    return db.query(RoomType).filter(RoomType.hotel_id == hotel_id, RoomType.is_active.is_(True)).order_by(RoomType.name).all()

@router.patch("/room-types/{room_type_id}", response_model=RoomTypeOut)
def update_room_type(room_type_id: int, payload: RoomTypeUpdate, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    item = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if not item: raise HTTPException(status_code=404, detail="Room type not found")
    hotel = _hotel_or_404(db, item.hotel_id)
    if not _can_manage_hotel(user, hotel): raise HTTPException(status_code=403, detail="You cannot manage this hotel")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item

@router.delete("/room-types/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_type(room_type_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if not item: raise HTTPException(status_code=404, detail="Room type not found")
    hotel = _hotel_or_404(db, item.hotel_id)
    if not _can_manage_hotel(user, hotel): raise HTTPException(status_code=403, detail="You cannot manage this hotel")
    item.is_active = False
    db.commit()
    return None

@router.post("/hotels/{hotel_id}/amenities", response_model=HotelAmenityOut, status_code=status.HTTP_201_CREATED)
def create_amenity(hotel_id: int, payload: HotelAmenityCreate, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    hotel = _hotel_or_404(db, hotel_id)
    if not _can_manage_hotel(user, hotel): raise HTTPException(status_code=403, detail="You cannot manage this hotel")
    if db.query(HotelAmenity).filter(HotelAmenity.hotel_id == hotel_id, HotelAmenity.name == payload.name).first():
        raise HTTPException(status_code=409, detail="Amenity already exists")
    item = HotelAmenity(hotel_id=hotel_id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/hotels/{hotel_id}/amenities", response_model=list[HotelAmenityOut])
def list_amenities(hotel_id: int, db: Session = Depends(get_db)):
    hotel = _hotel_or_404(db, hotel_id)
    if hotel.status != "APPROVED": raise HTTPException(status_code=404, detail="Hotel not found")
    return db.query(HotelAmenity).filter(HotelAmenity.hotel_id == hotel_id).order_by(HotelAmenity.name).all()

@router.patch("/amenities/{amenity_id}", response_model=HotelAmenityOut)
def update_amenity(amenity_id: int, payload: HotelAmenityUpdate, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    item = db.query(HotelAmenity).filter(HotelAmenity.id == amenity_id).first()
    if not item: raise HTTPException(status_code=404, detail="Amenity not found")
    hotel = _hotel_or_404(db, item.hotel_id)
    if not _can_manage_hotel(user, hotel): raise HTTPException(status_code=403, detail="You cannot manage this hotel")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item

@router.delete("/amenities/{amenity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_amenity(amenity_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(HotelAmenity).filter(HotelAmenity.id == amenity_id).first()
    if not item: raise HTTPException(status_code=404, detail="Amenity not found")
    hotel = _hotel_or_404(db, item.hotel_id)
    if not _can_manage_hotel(user, hotel): raise HTTPException(status_code=403, detail="You cannot manage this hotel")
    db.delete(item); db.commit()
    return None

@router.get("/availability", response_model=AvailabilityOut)
def check_availability(room_id: int = Query(gt=0), check_in: date = Query(...),
                       check_out: date = Query(...), db: Session = Depends(get_db)):
    if check_out <= check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")
    room = db.query(Room).filter(Room.id == room_id, Room.is_active.is_(True)).first()
    if not room: raise HTTPException(status_code=404, detail="Active room not found")
    hotel = _hotel_or_404(db, room.hotel_id)
    if hotel.status != "APPROVED": raise HTTPException(status_code=404, detail="Room not found")
    start, end = datetime.combine(check_in, time.min), datetime.combine(check_out, time.min)
    overlap = db.query(Booking).filter(Booking.room_id == room_id,
        Booking.check_in < end, Booking.check_out > start,
        Booking.status.in_(["PENDING", "CONFIRMED"])).first()
    return AvailabilityOut(room_id=room_id, check_in=check_in.isoformat(),
        check_out=check_out.isoformat(), available=overlap is None)
