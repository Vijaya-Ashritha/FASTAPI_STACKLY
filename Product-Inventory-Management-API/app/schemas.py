
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    category_name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CategoryUpdate(BaseModel):
    category_name: str | None = Field(
        default=None, min_length=1, max_length=100
    )
    description: str | None = None


class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    description: str | None
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    product_name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    category_id: int = Field(gt=0)
    price: float = Field(gt=0, allow_inf_nan=False)
    quantity: int = Field(ge=0)


class ProductUpdate(BaseModel):
    product_name: str | None = Field(
        default=None, min_length=1, max_length=100
    )
    description: str | None = None
    category_id: int | None = Field(default=None, gt=0)
    price: float | None = Field(
        default=None, gt=0, allow_inf_nan=False
    )
    quantity: int | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    description: str | None
    category_id: int
    price: float
    quantity: int
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryValueResponse(BaseModel):
    total_inventory_value: float
