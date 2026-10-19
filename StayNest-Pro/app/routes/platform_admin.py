import csv
import io
from datetime import date, datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import Booking, Hotel, Room
from app.models.user import User
from app.models.platform_admin import (
    AuditLog, HotelSubscription, HotelVerificationDocument, SubscriptionPlan
)
from app.schemas.platform_admin import (
    SubscriptionPlanCreate, SubscriptionPlanOut,
    VerificationDecision, VerificationDocumentCreate
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Dashboard, Moderation, Reports, Audit, Plans"])


def _admin(user: User):
    if str(getattr(user, "role", "")).upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Administrator access required")


def _audit(db: Session, user: User, action: str, entity_type: str,
           entity_id: int | None = None, reason: str | None = None, details: str | None = None):
    db.add(AuditLog(
        actor_user_id=getattr(user, "id", None), action=action,
        entity_type=entity_type, entity_id=entity_id, reason=reason, details=details
    ))


# Module 36: Admin dashboard
@router.get("/dashboard")
def admin_dashboard(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    date_from: date | None = None,
    date_to: date | None = None,
    hotel_id: int | None = Query(default=None, ge=1),
    status: str | None = None,
):
    _admin(user)
    booking_query = db.query(Booking)
    if date_from:
        booking_query = booking_query.filter(Booking.check_in >= datetime.combine(date_from, time.min))
    if date_to:
        booking_query = booking_query.filter(Booking.check_in < datetime.combine(date_to, time.max))
    if hotel_id:
        booking_query = booking_query.join(Room, Booking.room_id == Room.id).filter(Room.hotel_id == hotel_id)
    if status:
        booking_query = booking_query.filter(Booking.status == status.upper())

    paid_query = booking_query.filter(Booking.payment_status == "PAID")
    revenue = paid_query.with_entities(func.coalesce(func.sum(Booking.total_amount), 0)).scalar()
    active_count = booking_query.filter(Booking.status.in_(["PENDING", "CONFIRMED", "CHECKED_IN"])).count()
    return {
        "customers": db.query(User).filter(func.upper(User.role) == "CUSTOMER").count(),
        "hotels": db.query(Hotel).count(),
        "rooms": db.query(Room).count(),
        "bookings": booking_query.count(),
        "active_reservations": active_count,
        "paid_booking_revenue": float(revenue or 0),
        "filters": {"date_from": date_from, "date_to": date_to, "hotel_id": hotel_id, "status": status},
    }


# Module 37: Hotel verification and moderation
@router.post("/hotels/{hotel_id}/verification-documents")
def submit_verification_document(
    hotel_id: int, body: VerificationDocumentCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    _admin(user)
    if db.get(Hotel, hotel_id) is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    doc = HotelVerificationDocument(hotel_id=hotel_id, document_type=body.document_type,
                                    file_url=body.file_url, status="PENDING")
    db.add(doc)
    _audit(db, user, "VERIFICATION_DOCUMENT_ADDED", "HotelVerificationDocument", reason=body.document_type,
           details=f"hotel_id={hotel_id}")
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "hotel_id": doc.hotel_id, "document_type": doc.document_type,
            "file_url": doc.file_url, "status": doc.status, "created_at": doc.created_at}


@router.get("/verification-documents")
def list_verification_documents(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    status: str = "PENDING",
    hotel_id: int | None = Query(default=None, ge=1),
):
    _admin(user)
    q = db.query(HotelVerificationDocument).filter(
        HotelVerificationDocument.status == status.upper()
    )
    if hotel_id:
        q = q.filter(HotelVerificationDocument.hotel_id == hotel_id)
    rows = q.order_by(HotelVerificationDocument.created_at.desc()).limit(500).all()
    return [{"id": r.id, "hotel_id": r.hotel_id, "document_type": r.document_type,
             "file_url": r.file_url, "status": r.status, "review_reason": r.review_reason,
             "created_at": r.created_at, "reviewed_at": r.reviewed_at} for r in rows]


@router.post("/verification-documents/{document_id}/decision")
def decide_verification_document(
    document_id: int, body: VerificationDecision,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    _admin(user)
    doc = db.get(HotelVerificationDocument, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Verification document not found")
    if doc.status != "PENDING":
        raise HTTPException(status_code=409, detail="Document has already been reviewed")
    doc.status = body.decision
    doc.review_reason = body.reason
    doc.reviewed_by = user.id
    doc.reviewed_at = datetime.utcnow()
    _audit(db, user, f"VERIFICATION_{body.decision}", "HotelVerificationDocument",
           document_id, body.reason, f"hotel_id={doc.hotel_id}")
    db.commit()
    return {"id": doc.id, "status": doc.status, "review_reason": doc.review_reason}


@router.post("/hotels/{hotel_id}/moderation")
def moderate_hotel(
    hotel_id: int, body: VerificationDecision,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    _admin(user)
    hotel = db.get(Hotel, hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    decision = body.decision
    if hasattr(hotel, "status"):
        hotel.status = decision if decision in {"APPROVED", "REJECTED"} else "SUSPENDED"
    elif hasattr(hotel, "is_approved"):
        hotel.is_approved = decision == "APPROVED"
        if decision == "REJECTED" and hasattr(hotel, "is_active"):
            hotel.is_active = False
    elif hasattr(hotel, "is_active"):
        hotel.is_active = decision == "APPROVED"
    else:
        raise HTTPException(status_code=409, detail="Hotel model has no supported moderation status field")
    _audit(db, user, f"HOTEL_{decision}", "Hotel", hotel_id, body.reason)
    db.commit()
    return {"hotel_id": hotel_id, "decision": decision, "reason": body.reason}


# Module 38: Reports and CSV export (XLSX/PDF can be added when export dependencies are configured)
@router.get("/reports/bookings.csv")
def export_booking_report(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    date_from: date | None = None,
    date_to: date | None = None,
    hotel_id: int | None = Query(default=None, ge=1),
    status: str | None = None,
):
    _admin(user)
    q = db.query(Booking, Room).join(Room, Booking.room_id == Room.id)
    if date_from:
        q = q.filter(Booking.check_in >= datetime.combine(date_from, time.min))
    if date_to:
        q = q.filter(Booking.check_in < datetime.combine(date_to, time.max))
    if hotel_id:
        q = q.filter(Room.hotel_id == hotel_id)
    if status:
        q = q.filter(Booking.status == status.upper())
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["booking_id", "customer_id", "hotel_id", "room_id", "check_in", "check_out",
                     "status", "payment_status", "guests", "total_amount"])
    for booking, room in q.order_by(Booking.created_at.desc()).limit(10000).all():
        writer.writerow([booking.id, booking.customer_id, room.hotel_id, booking.room_id,
                         booking.check_in.isoformat() if booking.check_in else "",
                         booking.check_out.isoformat() if booking.check_out else "",
                         booking.status, booking.payment_status, booking.guests, booking.total_amount])
    output.seek(0)
    _audit(db, user, "REPORT_EXPORTED", "BookingReport", details="format=csv")
    db.commit()
    filename = f"staynest-bookings-{date.today().isoformat()}.csv"
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/reports/summary")
def report_summary(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    date_from: date | None = None,
    date_to: date | None = None,
):
    _admin(user)
    q = db.query(Booking)
    if date_from:
        q = q.filter(Booking.check_in >= datetime.combine(date_from, time.min))
    if date_to:
        q = q.filter(Booking.check_in < datetime.combine(date_to, time.max))
    rows = q.all()
    paid = [r for r in rows if r.payment_status == "PAID"]
    return {
        "period": {"date_from": date_from, "date_to": date_to},
        "bookings": len(rows),
        "paid_bookings": len(paid),
        "revenue": round(sum(float(r.total_amount or 0) for r in paid), 2),
        "status_counts": {key: sum(1 for r in rows if r.status == key)
                          for key in sorted({r.status for r in rows})},
    }


# Module 39: Audit logs and security monitoring
@router.get("/audit-logs")
def list_audit_logs(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    action: str | None = None,
    entity_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
):
    _admin(user)
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    return [{"id": r.id, "actor_user_id": r.actor_user_id, "action": r.action,
             "entity_type": r.entity_type, "entity_id": r.entity_id, "reason": r.reason,
             "details": r.details, "created_at": r.created_at}
            for r in q.order_by(AuditLog.created_at.desc()).limit(limit).all()]


# Module 40: Subscription plan management
@router.post("/subscription-plans", response_model=SubscriptionPlanOut, status_code=201)
def create_subscription_plan(
    body: SubscriptionPlanCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    _admin(user)
    if db.query(SubscriptionPlan).filter(func.upper(SubscriptionPlan.name) == body.name.upper()).first():
        raise HTTPException(status_code=409, detail="Subscription plan already exists")
    plan_data = body.model_dump()
    plan_data["name"] = body.name.upper()
    plan = SubscriptionPlan(**plan_data)
    db.add(plan)
    _audit(db, user, "SUBSCRIPTION_PLAN_CREATED", "SubscriptionPlan", reason=plan.name)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/subscription-plans", response_model=list[SubscriptionPlanOut])
def list_subscription_plans(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    include_inactive: bool = False,
):
    _admin(user)
    q = db.query(SubscriptionPlan)
    if not include_inactive:
        q = q.filter(SubscriptionPlan.is_active.is_(True))
    return q.order_by(SubscriptionPlan.price.asc()).all()


@router.patch("/subscription-plans/{plan_id}/deactivate")
def deactivate_subscription_plan(
    plan_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    _admin(user)
    plan = db.get(SubscriptionPlan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    if db.query(HotelSubscription).filter(
        HotelSubscription.plan_id == plan_id, HotelSubscription.status == "ACTIVE"
    ).first():
        raise HTTPException(status_code=409, detail="Plan has active subscriptions and cannot be deactivated")
    plan.is_active = False
    _audit(db, user, "SUBSCRIPTION_PLAN_DEACTIVATED", "SubscriptionPlan", plan_id)
    db.commit()
    return {"id": plan.id, "is_active": plan.is_active}
