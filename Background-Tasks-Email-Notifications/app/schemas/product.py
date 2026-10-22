
from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    stock_quantity: int = Field(ge=0)
    reorder_level: int = Field(default=10, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    stock_quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    stock_quantity: int
    reorder_level: int

    model_config = ConfigDict(from_attributes=True)
