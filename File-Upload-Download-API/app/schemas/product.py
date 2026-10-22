from pydantic import BaseModel, ConfigDict, Field

from app.schemas.file import FileMetadataResponse


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class ProductResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    image_id: int | None
    image: FileMetadataResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int