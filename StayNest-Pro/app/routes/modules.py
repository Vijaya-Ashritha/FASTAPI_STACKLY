from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.models.domain import FeatureRecord
from app.schemas.domain import FeatureRecordCreate
router=APIRouter(prefix="/api/v1/modules",tags=["Additional Platform Modules"])
MODULES={
 "room-types": "Room Type Management", "amenities": "Hotel Amenities", "gallery": "Hotel Details and Gallery",
 "guests": "Guest Management", "payments": "Payment records (simulation only)", "invoices": "Invoices and Receipts", "refunds": "Cancellation and Refund Requests",
 "coupons": "Coupons and Discounts", "reviews": "Reviews and Ratings", "wishlists": "Wishlist", "recommendations": "AI Recommendations metadata",
 "travel-assistant": "Travel Assistant conversations", "support-tickets": "Customer Support", "conversations": "AI Conversation History",
 "notifications": "Notifications", "messages": "Messaging", "housekeeping": "Housekeeping", "staff": "Staff Management",
 "check-ins": "Check-in records", "check-outs": "Check-out records", "hotel-services": "Hotel Services", "room-service": "Room Service",
 "maintenance": "Maintenance Requests", "owner-dashboard": "Hotel Owner Dashboard snapshots", "customer-dashboard": "Customer Dashboard snapshots",
 "admin-dashboard": "Admin Dashboard snapshots", "moderation": "Verification and Moderation", "reports": "Reports and Export",
 "audit-logs": "Audit Logs and Security Monitoring", "subscription-plans": "Hotel Subscription Plans", "subscription-payments": "Subscription Payments",
 "dynamic-pricing": "Dynamic Pricing rules", "loyalty": "Loyalty and Rewards", "locations": "Location Services", "schedules": "Calendar and Scheduler",
 "financial-records": "Financial Management", "business-intelligence": "Business Intelligence", "fraud-alerts": "Fraud Detection and Security",
 "system-config": "System Configuration", "admin-tools": "Advanced Administration"
}
ADMIN_ONLY={"moderation","audit-logs","system-config","admin-tools","fraud-alerts"}
@router.get("/catalog")
def module_catalog(): return {"modules": [{"key":k,"name":v,"storage":"FeatureRecord starter CRUD"} for k,v in MODULES.items()]}
def serialize(x): return {"id":x.id,"module":x.module,"owner_id":x.owner_id,"data":x.payload,"created_at":x.created_at}
@router.post("/{module_key}",status_code=201)
def create_record(module_key:str,body:FeatureRecordCreate,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(get_current_user)]):
    if module_key not in MODULES: raise HTTPException(404,"Unknown module key. See /api/v1/modules/catalog")
    if module_key in ADMIN_ONLY and user.role!="ADMIN": raise HTTPException(403,"Admin role required")
    row=FeatureRecord(module=module_key,owner_id=user.id,payload=body.data); db.add(row); db.commit(); db.refresh(row); return serialize(row)
@router.get("/{module_key}")
def list_records(module_key:str,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(get_current_user)]):
    if module_key not in MODULES: raise HTTPException(404,"Unknown module key. See /api/v1/modules/catalog")
    q=db.query(FeatureRecord).filter(FeatureRecord.module==module_key)
    if user.role!="ADMIN": q=q.filter(FeatureRecord.owner_id==user.id)
    return [serialize(x) for x in q.order_by(FeatureRecord.id.desc()).limit(500).all()]
@router.get("/{module_key}/{record_id}")
def get_record(module_key:str,record_id:int,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(get_current_user)]):
    row=db.query(FeatureRecord).filter_by(id=record_id,module=module_key).first()
    if not row: raise HTTPException(404,"Record not found")
    if user.role!="ADMIN" and row.owner_id!=user.id: raise HTTPException(403,"You cannot access this record")
    return serialize(row)
@router.put("/{module_key}/{record_id}")
def update_record(module_key:str,record_id:int,body:FeatureRecordCreate,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(get_current_user)]):
    row=db.query(FeatureRecord).filter_by(id=record_id,module=module_key).first()
    if not row: raise HTTPException(404,"Record not found")
    if user.role!="ADMIN" and row.owner_id!=user.id: raise HTTPException(403,"You cannot update this record")
    if module_key in ADMIN_ONLY and user.role!="ADMIN": raise HTTPException(403,"Admin role required")
    row.payload=body.data; db.commit(); db.refresh(row); return serialize(row)
@router.delete("/{module_key}/{record_id}",status_code=204)
def delete_record(module_key:str,record_id:int,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(get_current_user)]):
    row=db.query(FeatureRecord).filter_by(id=record_id,module=module_key).first()
    if not row: raise HTTPException(404,"Record not found")
    if user.role!="ADMIN" and row.owner_id!=user.id: raise HTTPException(403,"You cannot delete this record")
    if module_key in ADMIN_ONLY and user.role!="ADMIN": raise HTTPException(403,"Admin role required")
    db.delete(row); db.commit(); return None
