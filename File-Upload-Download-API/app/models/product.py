from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    image_id: Mapped[int | None] = mapped_column(
        ForeignKey("file_metadata.id", ondelete="SET NULL"),
        nullable=True,
    )

    image: Mapped["FileMetadata | None"] = relationship(
        back_populates="products",
    )