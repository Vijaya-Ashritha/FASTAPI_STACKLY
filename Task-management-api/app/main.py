from fastapi import FastAPI

from app.database import create_table
from app.routes.task import router


app = FastAPI(title="Task Management API")


create_table()

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Task Management API is running"
    }