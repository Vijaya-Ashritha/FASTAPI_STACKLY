from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.domain import Hotel, Room
from app.models.user import User
from app.schemas.domain import RoomCreate, RoomOut, RoomUpdate

router = APIRouter(prefix="/api/v1/rooms", tags=["Rooms and Availability"])


def ensure_room_manager(user: User, hotel: Hotel) -> None:
    if user.role != "ADMIN" and hotel.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this hotel's rooms")


@router.post("", response_model=RoomOut, status_code=201)
def create_room(
    body: RoomCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_roles("HOTEL_OWNER", "ADMIN"))],
):
    hotel = db.get(Hotel, body.hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    ensure_room_manager(user, hotel)

    room = Room(**body.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("", response_model=list[RoomOut])
def list_rooms(
    db: Annotated[Session, Depends(get_db)],
    hotel_id: int | None = Query(default=None, gt=0),
    room_type: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    query = (
        db.query(Room)
        .join(Hotel, Room.hotel_id == Hotel.id)
        .filter(Room.is_active.is_(True), Hotel.status == "APPROVED")
    )
    if hotel_id is not None:
        query = query.filter(Room.hotel_id == hotel_id)
    if room_type:
        query = query.filter(Room.room_type.ilike(f"%{room_type.strip()}%"))
    if min_price is not None:
        query = query.filter(Room.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(Room.price_per_night <= max_price)
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price cannot exceed max_price")
    return query.order_by(Room.id.desc()).offset(offset).limit(limit).all()


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db: Annotated[Session, Depends(get_db)]):
    room = db.get(Room, room_id)
    if not room or not room.is_active:
        raise HTTPException(status_code=404, detail="Active room not found")
    hotel = db.get(Hotel, room.hotel_id)
    if not hotel or hotel.status != "APPROVED":
        raise HTTPException(status_code=404, detail="Room not found in an approved hotel")
    return room


@router.patch("/{room_id}", response_model=RoomOut)
def update_room(
    room_id: int,
    body: RoomUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    hotel = db.get(Hotel, room.hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    ensure_room_manager(user, hotel)

    changes = body.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in changes.items():
        setattr(room, key, value)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204)
def disable_room(
    room_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    hotel = db.get(Hotel, room.hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    ensure_room_manager(user, hotel)

    room.is_active = False
    db.commit()
    return None
