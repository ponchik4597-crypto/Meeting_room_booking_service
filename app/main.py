from fastapi import FastAPI

from app.booking.routers import router as booking_router
from app.room.routers import router as room_router
from app.slot.routers import router as slot_router
from app.user.routers import router as user_router

app = FastAPI(title="Meeting Room Booking Service")

app.include_router(user_router)
app.include_router(room_router)
app.include_router(slot_router)
app.include_router(booking_router)


@app.get("/")
def read_root():
    """эндпоинт проверки работоспособности сервиса"""
    return {"status": "ok", "message": "Meeting Room Booking API is running"}
