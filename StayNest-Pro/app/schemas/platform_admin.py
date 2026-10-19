from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class VerificationDocumentCreate(BaseModel):
    document_type: str = Field(min_length=2, max_length=80)
    file_url: str = Field(min_length=5, max_length=1000)


class VerificationDecision(BaseModel):
    decision: str = Field(pattern="^(APPROVED|REJECTED|SUSPENDED)$")
    reason: str | None = Field(default=None, max_length=2000)


class SubscriptionPlanCreate(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    billing_period: str = Field(default="MONTHLY", pattern="^(MONTHLY|YEARLY)$")
    price: float = Field(ge=0)
    listing_limit: int = Field(default=1, ge=1)
    analytics_enabled: bool = False
    description: str | None = None


class SubscriptionPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    billing_period: str
    price: float
    listing_limit: int
    analytics_enabled: bool
    description: str | None
    is_active: bool
