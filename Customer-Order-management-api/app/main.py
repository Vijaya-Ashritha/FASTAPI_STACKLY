from fastapi import FastAPI

from app.database import create_tables
from app.routes.customer import router as customer_router
from app.routes.order import router as order_router


app = FastAPI(title="Customer and Order Management API")


create_tables()


app.include_router(customer_router)
app.include_router(order_router)


@app.get("/")
def home():
    return {
        "message": "Customer and Order Management API is running"
    }