
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


def current_time():
    return datetime.now(timezone.utc)


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), default=current_time)

    products = relationship(
        "Product",
        back_populates="category",
    )


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    category_id = Column(
        Integer,
        ForeignKey("categories.category_id"),
        nullable=False,
    )

    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    created_date = Column(DateTime(timezone=True), default=current_time)
    updated_date = Column(
        DateTime(timezone=True),
        default=current_time,
        onupdate=current_time,
    )

    category = relationship(
        "Category",
        back_populates="products",
    )
