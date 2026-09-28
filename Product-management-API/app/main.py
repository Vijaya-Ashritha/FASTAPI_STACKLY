from fastapi import FastAPI

from app.database import create_table
from app.routes.product import router


app = FastAPI(title="Product Management API")


create_table()

app.include_router(router)


@app.get("/")
def home():
    return {"message": "Product Management API is running"}