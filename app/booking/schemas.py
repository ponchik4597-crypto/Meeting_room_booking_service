from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class BookingBase(BaseModel):
    slot_id: int
    date: date


class BookingCreate(BookingBase):
    pass


class BookingResponse(BookingBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SlotAvailability(BaseModel):
    slot_id: int
    time_start: time
    time_end: time
    is_free: bool
    booking_id: int | None = None


class RoomAvailabilityResponse(BaseModel):
    room_id: int
    room_name: str
    date: date
    slots: list[SlotAvailability]
