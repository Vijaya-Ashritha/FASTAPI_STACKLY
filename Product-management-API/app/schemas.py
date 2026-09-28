from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)


class ProductResponse(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: float
    quantity: int