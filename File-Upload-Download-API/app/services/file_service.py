
import logging
import re
import uuid
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.file_metadata import FileMetadata
from app.models.product import Product
from app.repositories import file_repository


logger = logging.getLogger(__name__)

ALLOWED_BY_KIND = {
    "product_image": {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    },
    "supplier_document": {
        ".pdf": "application/pdf",
    },
}


def safe_original_filename(filename: str) -> str:
    filename = filename.replace("\\", "/")
    name = Path(filename).name

    name = re.sub(
        r"[^A-Za-z0-9._ -]",
        "_",
        name,
    ).strip(" .")

    return (name or "uploaded_file")[:255]


def validate_file_content(
    data: bytes,
    extension: str,
    content_type: str,
) -> None:
    expected_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".pdf": "application/pdf",
    }

    if extension not in expected_types:
        raise HTTPException(
            status_code=415,
            detail="Only JPG, PNG, and PDF files are allowed",
        )

    expected_type = expected_types[extension]

    if content_type not in {
        expected_type,
        "application/octet-stream",
    }:
        raise HTTPException(
            status_code=415,
            detail="Content-Type does not match file extension",
        )

    if extension in {".jpg", ".jpeg", ".png"}:
        try:
            with Image.open(BytesIO(data)) as image:
                image.verify()
                actual_format = image.format

            valid_image = (
                extension in {".jpg", ".jpeg"}
                and actual_format == "JPEG"
            ) or (
                extension == ".png"
                and actual_format == "PNG"
            )

            if not valid_image:
                raise HTTPException(
                    status_code=415,
                    detail="Image content does not match extension",
                )

        except (UnidentifiedImageError, OSError):
            raise HTTPException(
                status_code=415,
                detail="Invalid or corrupted image file",
            )

    elif not data.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=415,
            detail="Invalid PDF signature",
        )


async def upload_file(
    db: Session,
    upload,
    user_id: int,
    file_kind: str,
) -> FileMetadata:
    if file_kind not in ALLOWED_BY_KIND:
        raise HTTPException(
            status_code=422,
            detail=(
                "file_kind must be product_image "
                "or supplier_document"
            ),
        )

    if not upload.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    original_filename = safe_original_filename(
        upload.filename
    )

    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_BY_KIND[file_kind]:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported extension for {file_kind}",
        )

    # Read no more than 5 MB + 1 byte to detect oversized uploads.
    data = await upload.read(settings.max_file_size + 1)

    try:
        if not data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        if len(data) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 5 MB limit",
            )

        validate_file_content(
            data,
            extension,
            upload.content_type or "application/octet-stream",
        )

        stored_filename = f"{uuid.uuid4().hex}{extension}"

        folder = (
            "products"
            if file_kind == "product_image"
            else "suppliers"
        )

        root = settings.upload_path
        destination_dir = (root / folder).resolve()
        destination_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            destination_dir / stored_filename
        ).resolve()

        if not destination.is_relative_to(root):
            raise HTTPException(
                status_code=400,
                detail="Invalid storage path",
            )

        relative_path = f"{folder}/{stored_filename}"

        # Store file bytes on disk, not in the database.
        destination.write_bytes(data)

        record = FileMetadata(
            original_filename=original_filename,
            stored_filename=stored_filename,
            relative_path=relative_path,
            content_type=ALLOWED_BY_KIND[file_kind][extension],
            file_size=len(data),
            file_kind=file_kind,
            uploaded_by=user_id,
        )

        try:
            file_repository.create_file(db, record)
        except Exception:
            db.rollback()
            destination.unlink(missing_ok=True)
            logger.exception(
                "Failed to save file metadata"
            )
            raise HTTPException(
                status_code=500,
                detail="Could not save uploaded file",
            )

        return record

    finally:
        await upload.close()


def get_owned_file_or_404(
    db: Session,
    file_id: int,
    user_id: int,
) -> FileMetadata:
    record = file_repository.get_owned_file(
        db,
        file_id,
        user_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    return record


def get_disk_path(record: FileMetadata) -> Path:
    root = settings.upload_path
    path = (root / record.relative_path).resolve()

    if not path.is_relative_to(root):
        raise HTTPException(
            status_code=400,
            detail="Invalid stored file path",
        )

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stored file is missing",
        )

    return path


def delete_owned_file(
    db: Session,
    record: FileMetadata,
) -> None:
    linked_product = db.scalar(
        select(Product.id)
        .where(Product.image_id == record.id)
        .limit(1)
    )

    if linked_product is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "File is linked to a product. "
                "Unlink the image before deleting it."
            ),
        )

    root = settings.upload_path
    path = (root / record.relative_path).resolve()

    if not path.is_relative_to(root):
        raise HTTPException(
            status_code=400,
            detail="Invalid stored file path",
        )

    # Delete metadata first, then remove the stored file.
    file_repository.delete_file_record(db, record)

    try:
        path.unlink(missing_ok=True)
    except OSError:
        logger.exception(
            "Metadata deleted but file cleanup failed"
        )