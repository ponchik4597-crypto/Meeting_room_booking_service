from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.booking.models import Booking
from app.booking.schemas import RoomAvailabilityResponse, SlotAvailability
from app.db.session import get_db
from app.room.models import Room
from app.room.schemas import RoomCreate, RoomResponse
from app.user.models import User

router = APIRouter()


@router.get("", response_model=list[RoomAvailabilityResponse])
async def get_rooms(
    date: date,
    session: AsyncSession = Depends(get_db),
):
    """Эндпоинт для получения списка комнат и их доступности на указанную дату"""
    statement = select(Room).options(selectinload(Room.slots))
    result = await session.execute(statement)
    rooms = result.scalars().all()

    booking_statement = select(Booking).where(Booking.date == date)
    booking_result = await session.execute(booking_statement)
    bookings = booking_result.scalars().all()

    bookings_map = {b.slot_id: b for b in bookings}

    response = []
    for room in rooms:
        slots_availability = []

        sorted_slots = sorted(room.slots, key=lambda s: s.time_start)
        for slot in sorted_slots:
            existing_booking = bookings_map.get(slot.id)

            slots_availability.append(
                SlotAvailability(
                    slot_id=slot.id,
                    time_start=slot.time_start,
                    time_end=slot.time_end,
                    is_free=existing_booking is None,
                    booking_id=existing_booking.id if existing_booking else None,
                )
            )

        response.append(
            RoomAvailabilityResponse(
                room_id=room.id,
                room_name=room.name,
                date=date,
                slots=slots_availability,
            )
        )
    return response


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: RoomCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Эндпоинт для создания новой переговорной комнаты"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может добавлять комнаты",
        )

    statement = select(Room).where(Room.name == room_in.name)
    result = await session.execute(statement)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Комната с названием '{room_in.name}' уже существует",
        )

    new_room = Room(name=room_in.name, capacity=room_in.capacity)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)

    return new_room
