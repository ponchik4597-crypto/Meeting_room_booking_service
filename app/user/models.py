import datetime
from typing import TYPE_CHECKING, Literal

from app.db.base import (
    Base,
    DateTime,
    Mapped,
    String,
    func,
    mapped_column,
    relationship,
)

if TYPE_CHECKING:
    from app.booking.models import Booking


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    login: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Literal["employee", "admin"]] = mapped_column(
        String(20), default="employee", nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
