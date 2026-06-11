from datetime import time

from pydantic import BaseModel, ConfigDict


class SlotBase(BaseModel):
    time_start: time
    time_end: time


class SlotCreate(SlotBase):
    room_id: int


class SlotResponse(SlotBase):
    id: int
    room_id: int

    model_config = ConfigDict(from_attributes=True)
