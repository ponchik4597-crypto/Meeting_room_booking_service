from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.booking.routers import router as booking_router
from app.config import settings
from app.db.base import Base
from app.db.session import engine
from app.room.routers import router as room_router
from app.slot.routers import router as slot_router
from app.user.routers import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.DB_HOST:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Meeting Room Booking Service",
    description="API для бронирования переговорных комнат",
    lifespan=lifespan,
)

app.include_router(user_router, prefix="/users", tags=["Пользователи"])
app.include_router(room_router, prefix="/rooms", tags=["Комнаты"])
app.include_router(slot_router, prefix="/slots", tags=["Слоты"])
app.include_router(booking_router, prefix="/bookings", tags=["Бронирования"])


@app.get("/", tags=["Системный эндпоинт"])
def read_root():
    """эндпоинт проверки работоспособности сервиса"""
    return {"status": "ok", "message": "Meeting Room Booking API is running"}
