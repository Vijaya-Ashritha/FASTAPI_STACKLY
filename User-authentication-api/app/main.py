from fastapi import FastAPI

from app.database import create_table
from app.routes.user import router


app = FastAPI(title="User Authentication API")


create_table()

app.include_router(router)


@app.get("/")
def home():
    return {"message": "User Authentication API is running"}