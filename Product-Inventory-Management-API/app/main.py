
from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes import categories, products

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Inventory Management API",
    description="Manage product categories, products, and inventory value.",
    version="1.0.0",
)

app.include_router(categories.router)
app.include_router(products.router)


@app.get("/", tags=["Home"])
def home():
    return {"message": "Product Inventory Management API is running"}
