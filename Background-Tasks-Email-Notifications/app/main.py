
from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, products


app = FastAPI(title=settings.app_name)

app.include_router(auth.router)
app.include_router(products.router)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "message": "Background Tasks and Email Notifications API",
        "status": "running",
    }
