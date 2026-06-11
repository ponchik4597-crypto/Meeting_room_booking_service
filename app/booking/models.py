import datetime

from app.db.base import (
    TYPE_CHECKING,
    Base,
    Date,
    DateTime,
    ForeignKey,
    Mapped,
    UniqueConstraint,
    dt_date,
    func,
    mapped_column,
    relationship,
)

if TYPE_CHECKING:
    from app.slot.models import Slot
    from app.user.models import User


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    slot_id: Mapped[int] = mapped_column(
        ForeignKey("slots.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[dt_date] = mapped_column(Date, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="bookings")
    slot: Mapped["Slot"] = relationship(back_populates="bookings")

    __table_args__ = (UniqueConstraint("slot_id", "date", name="uq_slot_date"),)
