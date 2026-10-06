from fastapi import FastAPI

from app.database import create_tables
from app.routes.category import router as category_router
from app.routes.expenses import router as expense_router


app = FastAPI(title="Expense Management API")


create_tables()

app.include_router(category_router)
app.include_router(expense_router)


@app.get("/")
def home():
    return {
        "message": "Expense Management API is running"
    }