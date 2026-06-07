from app.db.base import (
    TYPE_CHECKING,
    Base,
    DateTime,
    ForeignKey,
    Mapped,
    Time,
    datetime,
    dt_time,
    func,
    mapped_column,
    relationship,
)

if TYPE_CHECKING:
    from app.db.models.booking import Booking
    from app.db.models.room import Room


class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    time_start: Mapped[dt_time] = mapped_column(Time, nullable=False)
    time_end: Mapped[dt_time] = mapped_column(Time, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    room: Mapped["Room"] = relationship(back_populates="slots")
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="slot", cascade="all, delete-orphan"
    )
