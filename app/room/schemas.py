from pydantic import BaseModel, ConfigDict, Field

from app.slot.schemas import SlotResponse


class RoomBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    capacity: int = Field(..., gt=0)


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int
    slots: list[SlotResponse] = []

    model_config = ConfigDict(from_attributes=True)
