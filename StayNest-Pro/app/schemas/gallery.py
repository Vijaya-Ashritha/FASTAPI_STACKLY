from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class GalleryImageCreate(BaseModel):
    image_url: HttpUrl
    caption: str | None = Field(default=None, max_length=255)
    alt_text: str | None = Field(default=None, max_length=255)


class GalleryImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel_id: int
    image_url: str
    caption: str | None
    alt_text: str | None
    created_at: datetime
