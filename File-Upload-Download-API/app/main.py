from fastapi import FastAPI

from app.api.files import router as files_router
from app.api.products import router as products_router
from app.core.config import settings

app = FastAPI(
    title="File Upload & Download API",
    description=(
        "Upload, validate, list, download and delete "
        "product images and supplier PDF documents. "
        "Protected endpoints require a Bearer JWT."
    ),
    version="1.0.0",
)

app.include_router(files_router)
app.include_router(products_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def create_upload_directories():
    (settings.upload_path / "products").mkdir(
        parents=True,
        exist_ok=True,
    )

    (settings.upload_path / "suppliers").mkdir(
        parents=True,
        exist_ok=True,
    )
