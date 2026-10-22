from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


FileKind = Literal["product_image", "supplier_document"]


class FileMetadataResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    relative_path: str
    content_type: str
    file_size: int
    file_kind: FileKind
    uploaded_by: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    items: list[FileMetadataResponse]
    total: int
    page: int
    page_size: int


class FileUploadResponse(BaseModel):
    message: str
    file: FileMetadataResponse


class ProductImageAssociation(BaseModel):
    image_id: int = Field(gt=0)