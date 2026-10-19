"""Pydantic schemas for engagement endpoints.

This file keeps the Batch 5 schema names used by existing tests and adds the
Batch 9 guest-profile, review, favorites, and notification schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewCreate(BaseModel):
    # hotel_id remains optional for backwards-compatible schema construction;
    # the HTTP endpoint requires it before saving a review.
    hotel_id: Optional[int] = Field(default=None, gt=0)
    booking_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = Field(default="", max_length=120)
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    hotel_id: int
    user_id: int
    booking_id: int
    rating: int
    title: str
    comment: str
    is_published: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content must not be blank")
        return value


class RecommendationRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=20)


class TravelAssistantRequest(BaseModel):
    destination: str = Field(min_length=1, max_length=120)
    nights: int = Field(ge=1, le=60)


class SupportChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Support message must not be blank")
        return value


class GuestProfileUpdate(BaseModel):
    phone: Optional[str] = Field(default=None, max_length=40)
    date_of_birth: Optional[str] = Field(default=None, max_length=10)
    preferred_language: Optional[str] = Field(default=None, max_length=30)
    special_requests: Optional[str] = None


class GuestProfileOut(GuestProfileUpdate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FavoriteOut(BaseModel):
    id: int
    user_id: int
    hotel_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(BaseModel):
    user_id: int = Field(gt=0)
    category: str = Field(default="GENERAL", max_length=40)
    title: str = Field(max_length=160)
    message: str = Field(min_length=1)


class NotificationOut(BaseModel):
    id: int
    user_id: int
    category: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
