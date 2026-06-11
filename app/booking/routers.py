from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.booking.models import Booking
from app.booking.schemas import BookingCreate, BookingResponse
from app.db.session import get_db
from app.slot.models import Slot
from app.user.models import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if booking_in.date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя забронировать на прошедщую дату",
        )

    slot_statement = select(Slot).where(Slot.id == booking_in.slot_id)
    slot_result = await session.execute(slot_statement)
    slot = slot_result.scalar_one_or_none()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Слот с id {booking_in.slot_id} не найден",
        )

    new_booking = Booking(
        user_id=current_user.id, slot_id=booking_in.slot_id, date=booking_in.date
    )

    try:
        session.add(new_booking)
        await session.commit()
        await session.refresh(new_booking)
        return new_booking
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Этот слот занят"
        )


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено"
        )
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для отмены"
        )
    await session.delete(booking)
    await session.commit()
