from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.engagement import GuestProfile, HotelReview, FavoriteHotel, UserNotification
from app.schemas.engagement import (
    GuestProfileUpdate, GuestProfileOut, ReviewCreate, ReviewOut,
    FavoriteOut, NotificationCreate, NotificationOut
)

router = APIRouter(tags=["Guest engagement (Batch 9)"])


def _owner_or_admin(requested_user_id: int, current_user: User) -> None:
    if current_user.id != requested_user_id and str(current_user.role).upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="You can only access your own account data")


def _require_admin(current_user: User) -> None:
    if str(current_user.role).upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Administrator access required")

# These endpoints accept an explicit user_id because the project's authentication
# dependency varies by deployment. Bind user_id to the JWT principal before production.

@router.get("/api/v1/guest-profiles/{user_id}", response_model=GuestProfileOut)
def get_guest_profile(user_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    _owner_or_admin(user_id, current_user)
    obj = db.query(GuestProfile).filter(GuestProfile.user_id == user_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Guest profile not found")
    return obj

@router.put("/api/v1/guest-profiles/{user_id}", response_model=GuestProfileOut)
def upsert_guest_profile(user_id: int, payload: GuestProfileUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    _owner_or_admin(user_id, current_user)
    obj = db.query(GuestProfile).filter(GuestProfile.user_id == user_id).first()
    values = payload.model_dump(exclude_unset=True)
    if obj is None:
        obj = GuestProfile(user_id=user_id, **values)
        db.add(obj)
    else:
        for key, value in values.items():
            setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.post("/api/v1/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(payload: ReviewCreate, user_id: int = Query(gt=0), db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    _owner_or_admin(user_id, current_user)
    if payload.hotel_id is None:
        raise HTTPException(status_code=422, detail="hotel_id is required")
    obj = HotelReview(
        user_id=user_id,
        hotel_id=payload.hotel_id,
        booking_id=payload.booking_id,
        rating=payload.rating,
        title=payload.title or "",
        comment=payload.comment or "",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/api/v1/hotels/{hotel_id}/reviews", response_model=list[ReviewOut])
def list_hotel_reviews(hotel_id: int, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return db.query(HotelReview).filter(
        HotelReview.hotel_id == hotel_id, HotelReview.is_published.is_(True)
    ).order_by(HotelReview.created_at.desc()).offset(offset).limit(limit).all()

@router.post("/api/v1/favorites/{user_id}/{hotel_id}", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(user_id: int, hotel_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    _owner_or_admin(user_id, current_user)
    obj = FavoriteHotel(user_id=user_id, hotel_id=hotel_id)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Hotel is already in favorites")
    db.refresh(obj)
    return obj

@router.get("/api/v1/favorites/{user_id}", response_model=list[FavoriteOut])
def list_favorites(user_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    _owner_or_admin(user_id, current_user)
    return db.query(FavoriteHotel).filter(FavoriteHotel.user_id == user_id).order_by(FavoriteHotel.created_at.desc()).all()

@router.delete("/api/v1/favorites/{user_id}/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(user_id: int, hotel_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    _owner_or_admin(user_id, current_user)
    obj = db.query(FavoriteHotel).filter(FavoriteHotel.user_id == user_id, FavoriteHotel.hotel_id == hotel_id).first()
    if obj is None:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(obj)
    db.commit()
    return None

@router.post("/api/v1/admin/notifications", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    obj = UserNotification(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/api/v1/notifications/{user_id}", response_model=list[NotificationOut])
def list_notifications(user_id: int, unread_only: bool = False, limit: int = Query(50, ge=1, le=100),
                        db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _owner_or_admin(user_id, current_user)
    q = db.query(UserNotification).filter(UserNotification.user_id == user_id)
    if unread_only:
        q = q.filter(UserNotification.is_read.is_(False))
    return q.order_by(UserNotification.created_at.desc()).limit(limit).all()

@router.patch("/api/v1/notifications/{user_id}/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(user_id: int, notification_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    _owner_or_admin(user_id, current_user)
    obj = db.query(UserNotification).filter(
        UserNotification.user_id == user_id, UserNotification.id == notification_id
    ).first()
    if obj is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    obj.is_read = True
    db.commit()
    db.refresh(obj)
    return obj
