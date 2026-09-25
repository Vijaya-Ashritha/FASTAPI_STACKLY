from fastapi import FastAPI

from app.database import create_table
from app.routes.employee import router as employee_router

app = FastAPI(title="Employee Directory API")

@app.on_event("startup")
def startup():
    create_table()

app.include_router(employee_router)

@app.get("/")
def root():
    return{"message": "Employee Directory API is running"}