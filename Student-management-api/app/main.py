
from fastapi import FastAPI

from app.database import create_table
from app.routes.student import router


app = FastAPI(title="Student Management API")


create_table()

app.include_router(router)


@app.get("/")
def home():
    return {"message": "Student Management API is running"}