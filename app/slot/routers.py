from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db.session import get_db
from app.room.models import Room
from app.slot.models import Slot
from app.slot.schemas import SlotCreate, SlotResponse
from app.user.models import User

router = APIRouter(prefix="/slots", tags=["Slots"])


@router.post("", response_model=SlotResponse, status_code=status.HTTP_201_CREATED)
async def create_slot(
    slot_in: SlotCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор управляет слотами",
        )

    # валидация времени
    if slot_in.time_start >= slot_in.time_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время начала слота должно быть меньше времени его окончания",
        )

    # проверка существования комнаты
    room_statement = select(Room).where(Room.id == slot_in.room_id)
    room_result = await session.execute(room_statement)
    if not room_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Переговорная комната с ID {slot_in.room_id} не найдена",
        )
    conflict_statement = select(Slot).where(
        and_(
            Slot.room_id == slot_in.room_id,
            Slot.time_start < slot_in.time_end,
            Slot.time_end > slot_in.time_start,
        )
    )
    conflict_result = await session.execute(conflict_statement)
    if conflict_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Это время пересекается с уже существующим слотом",
        )

    new_slot = Slot(
        room_id=slot_in.room_id,
        time_start=slot_in.time_start,
        time_end=slot_in.time_end,
    )

    session.add(new_slot)
    await session.commit()
    await session.refresh(new_slot)
    return new_slot
