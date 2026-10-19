from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from app.core.config import settings
from app.db.session import Base, engine
from app.db import base as model_registry  # noqa: F401 - imports all SQLAlchemy models
from app.routes import auth, profiles, hotels, rooms, bookings, modules, catalog, commerce, engagement, operations
from app.routes.platform_admin import router as platform_admin_router
from app.routes.completion import router as completion_router

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, description="Backend-only hotel, resort and room booking management API.")

# For local development only. Use Alembic migrations for production deployments.
@app.on_event("startup")
def create_tables_for_development():
    if settings.DEBUG:
        Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(hotels.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(modules.router)
app.include_router(catalog.router)
app.include_router(commerce.router)
app.include_router(engagement.router)
app.include_router(operations.router)
app.include_router(platform_admin_router)
app.include_router(completion_router)

@app.get("/")
def root():
    return {"message": "Welcome to StayNest Pro API", "docs": "/docs"}

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}

@app.get("/ready", tags=["System"])
def readiness_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is not ready") from exc
    return {"status": "ready", "database": "reachable"}








