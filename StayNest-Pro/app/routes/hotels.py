from datetime import date, datetime, time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.models.domain import Booking, Hotel, Room
from app.models.gallery import GalleryImage
from app.schemas.domain import HotelCreate, HotelUpdate, HotelOut
from app.schemas.gallery import GalleryImageCreate, GalleryImageOut

router = APIRouter(prefix="/api/v1/hotels", tags=["Hotels", "Hotel Search", "Hotel Details and Gallery"])


def _hotel_or_404(db: Session, hotel_id: int) -> Hotel:
    item = db.get(Hotel, hotel_id)
    if not item:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return item


def _can_manage_hotel(user: User, hotel: Hotel) -> bool:
    return user.role == "ADMIN" or hotel.owner_id == user.id


@router.post("", response_model=HotelOut, status_code=status.HTTP_201_CREATED)
def create_hotel(body: HotelCreate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_roles("HOTEL_OWNER", "ADMIN"))]):
    item = Hotel(owner_id=user.id, **body.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


@router.get("/search")
def search_hotels(
    db: Annotated[Session, Depends(get_db)],
    name: str | None = Query(default=None, min_length=1, max_length=160),
    city: str | None = Query(default=None, min_length=1, max_length=100),
    country: str | None = Query(default=None, min_length=1, max_length=100),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    capacity: int | None = Query(default=None, ge=1, le=30),
    check_in: date | None = None,
    check_out: date | None = None,
    sort_by: str = Query(default="name", pattern="^(name|price|city|newest)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price cannot exceed max_price")
    if (check_in is None) != (check_out is None):
        raise HTTPException(status_code=422, detail="check_in and check_out must be provided together")
    if check_in is not None and check_out is not None and check_out <= check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")

    query = db.query(Hotel).filter(Hotel.status == "APPROVED")
    if name:
        query = query.filter(Hotel.name.ilike(f"%{name.strip()}%"))
    if city:
        query = query.filter(Hotel.city.ilike(f"%{city.strip()}%"))
    if country:
        query = query.filter(Hotel.country.ilike(f"%{country.strip()}%"))

    room_filters = [Room.hotel_id == Hotel.id, Room.is_active.is_(True)]
    if min_price is not None: room_filters.append(Room.price_per_night >= min_price)
    if max_price is not None: room_filters.append(Room.price_per_night <= max_price)
    if capacity is not None: room_filters.append(Room.capacity >= capacity)
    if check_in is not None and check_out is not None:
        start = datetime.combine(check_in, time.min)
        end = datetime.combine(check_out, time.min)
        conflict = db.query(Booking.id).filter(
            Booking.room_id == Room.id,
            Booking.status.in_(["PENDING", "CONFIRMED"]),
            Booking.check_in < end,
            Booking.check_out > start,
        ).exists()
        room_filters.append(~conflict)
    if any(v is not None for v in (min_price, max_price, capacity, check_in, check_out)):
        query = query.filter(db.query(Room.id).filter(*room_filters).exists())

    total = query.count()
    if sort_by == "price":
        price_subquery = db.query(Room.hotel_id, __import__('sqlalchemy').func.min(Room.price_per_night).label("starting_price")).filter(Room.is_active.is_(True)).group_by(Room.hotel_id).subquery()
        query = query.outerjoin(price_subquery, price_subquery.c.hotel_id == Hotel.id)
        sort_column = price_subquery.c.starting_price
    elif sort_by == "city": sort_column = Hotel.city
    elif sort_by == "newest": sort_column = Hotel.id
    else: sort_column = Hotel.name
    query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc(), Hotel.id.asc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [HotelOut.model_validate(h).model_dump() for h in items], "page": page, "page_size": page_size,
            "total": total, "pages": (total + page_size - 1) // page_size}


@router.get("")
def list_hotels(db: Annotated[Session, Depends(get_db)], city: str | None = None, q: str | None = None,
                status_filter: str | None = Query(default="APPROVED", alias="status")):
    query = db.query(Hotel)
    if city: query = query.filter(Hotel.city.ilike(f"%{city}%"))
    if q: query = query.filter(Hotel.name.ilike(f"%{q}%"))
    if status_filter: query = query.filter(Hotel.status == status_filter)
    return query.order_by(Hotel.id.desc()).all()


@router.get("/{hotel_id}/details")
def hotel_details(hotel_id: int, db: Annotated[Session, Depends(get_db)]):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.status == "APPROVED").first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    rooms = db.query(Room).filter(Room.hotel_id == hotel_id, Room.is_active.is_(True)).order_by(Room.price_per_night, Room.id).all()
    images = db.query(GalleryImage).filter(GalleryImage.hotel_id == hotel_id).order_by(GalleryImage.id).all()
    return {"hotel": HotelOut.model_validate(hotel).model_dump(),
            "active_rooms": [{"id": r.id, "hotel_id": r.hotel_id, "name": r.name, "room_type": r.room_type,
                              "capacity": r.capacity, "price_per_night": r.price_per_night,
                              "amenities": r.amenities} for r in rooms],
            "gallery": [GalleryImageOut.model_validate(i).model_dump() for i in images]}


@router.get("/{hotel_id}/gallery", response_model=list[GalleryImageOut])
def list_gallery(
    hotel_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    hotel = _hotel_or_404(db, hotel_id)

    return (
        db.query(GalleryImage)
        .filter(GalleryImage.hotel_id == hotel_id)
        .order_by(GalleryImage.id)
        .all()
    )

@router.post("/{hotel_id}/gallery", response_model=GalleryImageOut, status_code=status.HTTP_201_CREATED)
def add_gallery_image(hotel_id: int, body: GalleryImageCreate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    hotel = _hotel_or_404(db, hotel_id)
    if not _can_manage_hotel(user, hotel): raise HTTPException(status_code=403, detail="Only the hotel owner or admin can manage its gallery")
    item = GalleryImage(hotel_id=hotel_id, image_url=str(body.image_url), caption=body.caption, alt_text=body.alt_text)
    db.add(item); db.commit(); db.refresh(item)
    return item


@router.delete("/{hotel_id}/gallery/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gallery_image(hotel_id: int, image_id: int, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    hotel = _hotel_or_404(db, hotel_id)
    if not _can_manage_hotel(user, hotel): raise HTTPException(status_code=403, detail="Only the hotel owner or admin can manage its gallery")
    item = db.query(GalleryImage).filter(GalleryImage.id == image_id, GalleryImage.hotel_id == hotel_id).first()
    if not item: raise HTTPException(status_code=404, detail="Gallery image not found")
    db.delete(item); db.commit()
    return None


@router.get("/{hotel_id}", response_model=HotelOut)
def get_hotel(hotel_id: int, db: Annotated[Session, Depends(get_db)]):
    item = db.get(Hotel, hotel_id)
    if not item: raise HTTPException(status_code=404, detail="Hotel not found")
    return item


@router.patch("/{hotel_id}", response_model=HotelOut)
def update_hotel(hotel_id: int, body: HotelUpdate, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]):
    item = db.get(Hotel, hotel_id)
    if not item: raise HTTPException(status_code=404, detail="Hotel not found")
    if user.role != "ADMIN" and item.owner_id != user.id: raise HTTPException(status_code=403, detail="Only the owner or admin can update this hotel")
    for k, v in body.model_dump(exclude_unset=True).items(): setattr(item, k, v)
    db.commit(); db.refresh(item)
    return item


@router.post("/{hotel_id}/approve", response_model=HotelOut)
def approve_hotel(hotel_id: int, db: Annotated[Session, Depends(get_db)], admin: Annotated[User, Depends(require_roles("ADMIN"))]):
    item = db.get(Hotel, hotel_id)
    if not item: raise HTTPException(status_code=404, detail="Hotel not found")
    item.status = "APPROVED"; db.commit(); db.refresh(item)
    return item
