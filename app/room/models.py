import datetime

from app.db.base import (
    TYPE_CHECKING,
    Base,
    DateTime,
    Mapped,
    String,
    func,
    mapped_column,
    relationship,
)

if TYPE_CHECKING:
    from app.slot.models import Slot


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    slots: Mapped[list["Slot"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
