from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.repositories.file_repository import list_owned_files
from app.schemas.file import (
    FileListResponse,
    FileMetadataResponse,
    FileUploadResponse,
)
from app.services.file_service import (
    delete_owned_file,
    get_disk_path,
    get_owned_file_or_404,
    upload_file,
)


router = APIRouter(
    prefix="/api/v1/files",
    tags=["Files"],
)


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=201,
)
async def upload(
    file: UploadFile = File(...),
    file_kind: str = Query(
        ...,
        description="product_image or supplier_document",
    ),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    record = await upload_file(
        db,
        file,
        user_id,
        file_kind,
    )

    return {
        "message": "File uploaded successfully",
        "file": record,
    }


@router.get("", response_model=FileListResponse)
def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    file_kind: str | None = Query(
        None,
        pattern="^(product_image|supplier_document)$",
    ),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    items, total = list_owned_files(
        db,
        user_id,
        page,
        page_size,
        file_kind,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/{file_id}",
    response_model=FileMetadataResponse,
)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_owned_file_or_404(
        db,
        file_id,
        user_id,
    )


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    record = get_owned_file_or_404(
        db,
        file_id,
        user_id,
    )

    path = get_disk_path(record)

    return FileResponse(
        path=path,
        media_type=record.content_type,
        filename=record.original_filename,
    )


@router.delete("/{file_id}", status_code=204)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    record = get_owned_file_or_404(
        db,
        file_id,
        user_id,
    )

    delete_owned_file(db, record)

    return None
