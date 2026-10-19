
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import Booking, Hotel, Room
from app.models.operations import (
    HotelService,
    HotelStaffAssignment,
    HousekeepingTask,
    RoomServiceOrder,
    RoomServiceOrderItem,
)
from app.models.user import User
from app.schemas.operations import (
    HotelServiceCreate,
    HotelServiceOut,
    HotelServiceUpdate,
    HousekeepingTaskCreate,
    HousekeepingTaskOut,
    HousekeepingTaskUpdate,
    RoomServiceOrderCreate,
    RoomServiceOrderOut,
    RoomServiceOrderStatusUpdate,
    StaffAssignmentCreate,
    StaffAssignmentOut,
    StaffAssignmentUpdate,
)

router = APIRouter(tags=["Batch 6 - Hotel Operations"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

TASK_STATUSES = {"PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"}
ORDER_STATUSES = {
    "PLACED", "ACCEPTED", "PREPARING", "READY", "DELIVERED", "CANCELLED"
}


def _hotel_or_404(db: Session, hotel_id: int) -> Hotel:
    hotel = db.get(Hotel, hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel


def _is_hotel_owner_or_admin(user: User, hotel: Hotel) -> bool:
    return user.role == "ADMIN" or (
        user.role == "HOTEL_OWNER" and hotel.owner_id == user.id
    )


def _is_assigned_staff(db: Session, user: User, hotel_id: int) -> bool:
    if user.role != "HOTEL_STAFF":
        return False
    return (
        db.query(HotelStaffAssignment.id)
        .filter(
            HotelStaffAssignment.hotel_id == hotel_id,
            HotelStaffAssignment.user_id == user.id,
            HotelStaffAssignment.is_active.is_(True),
        )
        .first()
        is not None
    )


def _require_hotel_access(db: Session, user: User, hotel_id: int) -> Hotel:
    hotel = _hotel_or_404(db, hotel_id)
    if _is_hotel_owner_or_admin(user, hotel):
        return hotel
    if _is_assigned_staff(db, user, hotel_id):
        return hotel
    raise HTTPException(
        status_code=403,
        detail="You do not have access to this hotel's operations",
    )


def _require_hotel_manager(db: Session, user: User, hotel_id: int) -> Hotel:
    hotel = _hotel_or_404(db, hotel_id)
    if not _is_hotel_owner_or_admin(user, hotel):
        raise HTTPException(
            status_code=403,
            detail="Only the hotel owner or an admin can manage this resource",
        )
    return hotel


def _require_staff_assignment(
    db: Session, staff_id: int, hotel_id: int
) -> User:
    staff = db.get(User, staff_id)
    if staff is None or not staff.is_active or staff.role != "HOTEL_STAFF":
        raise HTTPException(
            status_code=422,
            detail="assigned_staff_id must identify an active hotel staff user",
        )
    assignment = (
        db.query(HotelStaffAssignment)
        .filter(
            HotelStaffAssignment.hotel_id == hotel_id,
            HotelStaffAssignment.user_id == staff_id,
            HotelStaffAssignment.is_active.is_(True),
        )
        .first()
    )
    if assignment is None:
        raise HTTPException(
            status_code=422,
            detail="Staff member must have an active assignment to this hotel",
        )
    return staff


def _booking_or_404(db: Session, booking_id: int) -> Booking:
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


def _order_payload(db: Session, order: RoomServiceOrder) -> dict:
    items = (
        db.query(RoomServiceOrderItem)
        .filter(RoomServiceOrderItem.order_id == order.id)
        .order_by(RoomServiceOrderItem.id.asc())
        .all()
    )
    return {
        "id": order.id,
        "booking_id": order.booking_id,
        "hotel_id": order.hotel_id,
        "room_id": order.room_id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "notes": order.notes,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": items,
    }


# Module 27: staff assignments

@router.post(
    "/api/v1/staff-assignments",
    response_model=StaffAssignmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_staff_assignment(
    body: StaffAssignmentCreate, db: DbSession, user: CurrentUser
):
    _require_hotel_manager(db, user, body.hotel_id)

    staff = db.get(User, body.user_id)
    if staff is None or not staff.is_active or staff.role != "HOTEL_STAFF":
        raise HTTPException(
            status_code=422,
            detail="user_id must identify an active HOTEL_STAFF user",
        )

    assignment = HotelStaffAssignment(
        hotel_id=body.hotel_id,
        user_id=body.user_id,
        assignment_role=body.assignment_role.strip().upper(),
        is_active=True,
        created_by=user.id,
    )
    db.add(assignment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This staff member is already assigned to this hotel",
        ) from exc
    db.refresh(assignment)
    return assignment


@router.get(
    "/api/v1/staff-assignments",
    response_model=list[StaffAssignmentOut],
)
def list_staff_assignments(
    db: DbSession,
    user: CurrentUser,
    hotel_id: int | None = Query(default=None, gt=0),
):
    query = db.query(HotelStaffAssignment)

    if hotel_id is not None:
        _require_hotel_access(db, user, hotel_id)
        query = query.filter(HotelStaffAssignment.hotel_id == hotel_id)

    if user.role == "ADMIN":
        pass
    elif user.role == "HOTEL_OWNER":
        owned_ids = [
            row[0]
            for row in db.query(Hotel.id)
            .filter(Hotel.owner_id == user.id)
            .all()
        ]
        query = query.filter(HotelStaffAssignment.hotel_id.in_(owned_ids))
    elif user.role == "HOTEL_STAFF":
        query = query.filter(HotelStaffAssignment.user_id == user.id)
    else:
        raise HTTPException(
            status_code=403, detail="You cannot view staff assignments"
        )

    return query.order_by(HotelStaffAssignment.id.desc()).limit(500).all()


@router.patch(
    "/api/v1/staff-assignments/{assignment_id}",
    response_model=StaffAssignmentOut,
)
def update_staff_assignment(
    assignment_id: int,
    body: StaffAssignmentUpdate,
    db: DbSession,
    user: CurrentUser,
):
    assignment = db.get(HotelStaffAssignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Staff assignment not found")

    _require_hotel_manager(db, user, assignment.hotel_id)
    changes = body.model_dump(exclude_unset=True)

    if "assignment_role" in changes and changes["assignment_role"] is not None:
        changes["assignment_role"] = changes["assignment_role"].strip().upper()

    for field, value in changes.items():
        setattr(assignment, field, value)

    db.commit()
    db.refresh(assignment)
    return assignment


# Module 26: housekeeping

@router.post(
    "/api/v1/housekeeping/tasks",
    response_model=HousekeepingTaskOut,
    status_code=status.HTTP_201_CREATED,
)
def create_housekeeping_task(
    body: HousekeepingTaskCreate, db: DbSession, user: CurrentUser
):
    _require_hotel_manager(db, user, body.hotel_id)

    room = db.get(Room, body.room_id)
    if room is None or room.hotel_id != body.hotel_id:
        raise HTTPException(
            status_code=422, detail="room_id must belong to hotel_id"
        )

    if body.assigned_staff_id is not None:
        _require_staff_assignment(db, body.assigned_staff_id, body.hotel_id)

    task = HousekeepingTask(
        hotel_id=body.hotel_id,
        room_id=body.room_id,
        assigned_staff_id=body.assigned_staff_id,
        created_by=user.id,
        task_type=body.task_type.strip().upper(),
        status="PENDING",
        notes=body.notes.strip(),
        scheduled_at=body.scheduled_at,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get(
    "/api/v1/housekeeping/tasks",
    response_model=list[HousekeepingTaskOut],
)
def list_housekeeping_tasks(
    db: DbSession,
    user: CurrentUser,
    hotel_id: int | None = Query(default=None, gt=0),
    task_status: str | None = Query(default=None, alias="status"),
):
    query = db.query(HousekeepingTask)

    if hotel_id is not None:
        _require_hotel_access(db, user, hotel_id)
        query = query.filter(HousekeepingTask.hotel_id == hotel_id)
    elif user.role == "ADMIN":
        pass
    elif user.role == "HOTEL_OWNER":
        owned_ids = [
            row[0]
            for row in db.query(Hotel.id)
            .filter(Hotel.owner_id == user.id)
            .all()
        ]
        query = query.filter(HousekeepingTask.hotel_id.in_(owned_ids))
    elif user.role == "HOTEL_STAFF":
        assigned_ids = [
            row[0]
            for row in db.query(HotelStaffAssignment.hotel_id)
            .filter(
                HotelStaffAssignment.user_id == user.id,
                HotelStaffAssignment.is_active.is_(True),
            )
            .all()
        ]
        query = query.filter(
            HousekeepingTask.hotel_id.in_(assigned_ids),
            HousekeepingTask.assigned_staff_id == user.id,
        )
    else:
        raise HTTPException(
            status_code=403, detail="You cannot view housekeeping tasks"
        )

    if task_status is not None:
        normalized = task_status.strip().upper()
        if normalized not in TASK_STATUSES:
            raise HTTPException(status_code=422, detail="Invalid task status")
        query = query.filter(HousekeepingTask.status == normalized)

    return query.order_by(HousekeepingTask.id.desc()).limit(500).all()


@router.patch(
    "/api/v1/housekeeping/tasks/{task_id}",
    response_model=HousekeepingTaskOut,
)
def update_housekeeping_task(
    task_id: int,
    body: HousekeepingTaskUpdate,
    db: DbSession,
    user: CurrentUser,
):
    task = db.get(HousekeepingTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Housekeeping task not found")

    hotel = _require_hotel_access(db, user, task.hotel_id)
    manager = _is_hotel_owner_or_admin(user, hotel)

    if not manager and task.assigned_staff_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Staff can update only tasks assigned to them",
        )

    changes = body.model_dump(exclude_unset=True)

    if "assigned_staff_id" in changes:
        if not manager:
            raise HTTPException(
                status_code=403, detail="Only managers can reassign tasks"
            )
        if changes["assigned_staff_id"] is not None:
            _require_staff_assignment(
                db, changes["assigned_staff_id"], task.hotel_id
            )

    if "status" in changes and changes["status"] is not None:
        normalized = changes["status"].strip().upper()
        if normalized not in TASK_STATUSES:
            raise HTTPException(status_code=422, detail="Invalid task status")
        changes["status"] = normalized

    for field, value in changes.items():
        setattr(task, field, value)

    if task.status == "COMPLETED":
        task.completed_at = datetime.now(timezone.utc)
    elif "status" in changes and task.status != "COMPLETED":
        task.completed_at = None

    db.commit()
    db.refresh(task)
    return task


# Module 29: hotel services catalog

@router.post(
    "/api/v1/hotels/{hotel_id}/services",
    response_model=HotelServiceOut,
    status_code=status.HTTP_201_CREATED,
)
def create_hotel_service(
    hotel_id: int, body: HotelServiceCreate, db: DbSession, user: CurrentUser
):
    _require_hotel_manager(db, user, hotel_id)

    if body.hotel_id != hotel_id:
        raise HTTPException(
            status_code=422,
            detail="Body hotel_id must match the URL hotel_id",
        )

    service = HotelService(
        hotel_id=hotel_id,
        name=body.name.strip(),
        description=body.description.strip(),
        price=body.price,
        currency=body.currency.upper(),
        is_available=body.is_available,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get(
    "/api/v1/hotels/{hotel_id}/services",
    response_model=list[HotelServiceOut],
)
def list_hotel_services(
    hotel_id: int,
    db: DbSession,
    user: CurrentUser,
):
    hotel = _hotel_or_404(db, hotel_id)
    query = db.query(HotelService).filter(HotelService.hotel_id == hotel_id)

    manager = bool(user and _is_hotel_owner_or_admin(user, hotel))
    staff = bool(user and _is_assigned_staff(db, user, hotel_id))
    if not manager and not staff:
        query = query.filter(HotelService.is_available.is_(True))

    return query.order_by(HotelService.name.asc()).all()


@router.patch(
    "/api/v1/services/{service_id}",
    response_model=HotelServiceOut,
)
def update_hotel_service(
    service_id: int,
    body: HotelServiceUpdate,
    db: DbSession,
    user: CurrentUser,
):
    service = db.get(HotelService, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Hotel service not found")

    _require_hotel_manager(db, user, service.hotel_id)
    changes = body.model_dump(exclude_unset=True)

    for field, value in changes.items():
        if isinstance(value, str):
            value = value.strip()
            if field == "currency":
                value = value.upper()
        setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service


# Module 30: room-service orders

@router.post(
    "/api/v1/room-service/orders",
    response_model=RoomServiceOrderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_room_service_order(
    body: RoomServiceOrderCreate, db: DbSession, user: CurrentUser
):
    booking = _booking_or_404(db, body.booking_id)

    if user.role != "ADMIN" and booking.customer_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the booking customer or an admin can place this order",
        )

    if booking.status != "CHECKED_IN":
        raise HTTPException(
            status_code=409,
            detail="Room-service orders require a checked-in booking",
        )

    room = db.get(Room, booking.room_id)
    if room is None:
        raise HTTPException(status_code=409, detail="Booking room was not found")

    service_ids = [item.service_id for item in body.items]
    if len(service_ids) != len(set(service_ids)):
        raise HTTPException(
            status_code=422,
            detail="Each service may appear only once; combine its quantity",
        )

    services = (
        db.query(HotelService)
        .filter(
            HotelService.id.in_(service_ids),
            HotelService.hotel_id == room.hotel_id,
            HotelService.is_available.is_(True),
        )
        .all()
    )
    service_map = {service.id: service for service in services}

    if len(service_map) != len(service_ids):
        raise HTTPException(
            status_code=422,
            detail="One or more services are unavailable or do not belong to the booking hotel",
        )

    total = round(
        sum(
            float(service_map[item.service_id].price) * item.quantity
            for item in body.items
        ),
        2,
    )

    order = RoomServiceOrder(
        booking_id=booking.id,
        hotel_id=room.hotel_id,
        room_id=room.id,
        customer_id=booking.customer_id,
        status="PLACED",
        total_amount=total,
        notes=body.notes.strip(),
    )
    db.add(order)
    db.flush()

    for item in body.items:
        service = service_map[item.service_id]
        unit_price = round(float(service.price), 2)
        db.add(
            RoomServiceOrderItem(
                order_id=order.id,
                service_id=service.id,
                service_name=service.name,
                quantity=item.quantity,
                unit_price=unit_price,
                line_total=round(unit_price * item.quantity, 2),
            )
        )

    db.commit()
    db.refresh(order)
    return _order_payload(db, order)


@router.get(
    "/api/v1/room-service/orders",
    response_model=list[RoomServiceOrderOut],
)
def list_room_service_orders(
    db: DbSession,
    user: CurrentUser,
    hotel_id: int | None = Query(default=None, gt=0),
):
    query = db.query(RoomServiceOrder)

    if user.role == "ADMIN":
        pass
    elif user.role == "CUSTOMER":
        query = query.filter(RoomServiceOrder.customer_id == user.id)
    elif user.role == "HOTEL_OWNER":
        owned_ids = [
            row[0]
            for row in db.query(Hotel.id)
            .filter(Hotel.owner_id == user.id)
            .all()
        ]
        query = query.filter(RoomServiceOrder.hotel_id.in_(owned_ids))
    elif user.role == "HOTEL_STAFF":
        assigned_ids = [
            row[0]
            for row in db.query(HotelStaffAssignment.hotel_id)
            .filter(
                HotelStaffAssignment.user_id == user.id,
                HotelStaffAssignment.is_active.is_(True),
            )
            .all()
        ]
        query = query.filter(RoomServiceOrder.hotel_id.in_(assigned_ids))
    else:
        raise HTTPException(
            status_code=403, detail="You cannot view room-service orders"
        )

    if hotel_id is not None:
        _require_hotel_access(db, user, hotel_id)
        query = query.filter(RoomServiceOrder.hotel_id == hotel_id)

    orders = query.order_by(RoomServiceOrder.id.desc()).limit(500).all()
    return [_order_payload(db, order) for order in orders]


@router.get(
    "/api/v1/room-service/orders/{order_id}",
    response_model=RoomServiceOrderOut,
)
def get_room_service_order(order_id: int, db: DbSession, user: CurrentUser):
    order = db.get(RoomServiceOrder, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Room-service order not found")

    if user.role == "CUSTOMER":
        allowed = order.customer_id == user.id
    elif user.role in {"ADMIN", "HOTEL_OWNER", "HOTEL_STAFF"}:
        hotel = _require_hotel_access(db, user, order.hotel_id)
        allowed = _is_hotel_owner_or_admin(user, hotel) or _is_assigned_staff(
            db, user, order.hotel_id
        )
    else:
        allowed = False

    if not allowed:
        raise HTTPException(
            status_code=403, detail="You cannot access this room-service order"
        )

    return _order_payload(db, order)


@router.patch(
    "/api/v1/room-service/orders/{order_id}/status",
    response_model=RoomServiceOrderOut,
)
def update_room_service_order_status(
    order_id: int,
    body: RoomServiceOrderStatusUpdate,
    db: DbSession,
    user: CurrentUser,
):
    order = db.get(RoomServiceOrder, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Room-service order not found")

    _require_hotel_access(db, user, order.hotel_id)
    normalized = body.status.strip().upper()

    if normalized not in ORDER_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid room-service order status")

    if order.status in {"DELIVERED", "CANCELLED"}:
        raise HTTPException(
            status_code=409,
            detail="A delivered or cancelled order cannot be changed",
        )

    order.status = normalized
    db.commit()
    db.refresh(order)
    return _order_payload(db, order)

