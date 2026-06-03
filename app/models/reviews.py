from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReviewModel(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now
    )
    grade: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    author: Mapped["User"] = relationship(
        "User", back_populates="reviews"
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="reviews"
    )
