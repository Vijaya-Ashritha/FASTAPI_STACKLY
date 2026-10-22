from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.file_metadata import FileMetadata


def create_file(db: Session, record: FileMetadata) -> FileMetadata:
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_file(
    db: Session,
    file_id: int,
) -> FileMetadata | None:
    return db.get(FileMetadata, file_id)


def get_owned_file(
    db: Session,
    file_id: int,
    user_id: int,
) -> FileMetadata | None:
    statement = select(FileMetadata).where(
        FileMetadata.id == file_id,
        FileMetadata.uploaded_by == user_id,
    )

    return db.scalar(statement)


def list_owned_files(
    db: Session,
    user_id: int,
    page: int,
    page_size: int,
    file_kind: str | None = None,
) -> tuple[list[FileMetadata], int]:
    statement = select(FileMetadata).where(
        FileMetadata.uploaded_by == user_id
    )

    count_statement = (
        select(func.count())
        .select_from(FileMetadata)
        .where(FileMetadata.uploaded_by == user_id)
    )

    if file_kind:
        statement = statement.where(
            FileMetadata.file_kind == file_kind
        )

        count_statement = count_statement.where(
            FileMetadata.file_kind == file_kind
        )

    statement = (
        statement
        .order_by(FileMetadata.uploaded_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    items = list(db.scalars(statement).all())
    total = int(db.scalar(count_statement) or 0)

    return items, total


def delete_file_record(
    db: Session,
    record: FileMetadata,
) -> None:
    db.delete(record)
    db.commit()
