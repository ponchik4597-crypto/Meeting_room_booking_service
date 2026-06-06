from fastapi import FastAPI

app = FastAPI(title="Meeting Room Booking Service")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Meeting Room Booking API is running"}


@app.get("/rooms")
def get_rooms():
    return [
        {"room_id": 1, "name": "Ocean", "capacity": 6},
        {"room_id": 2, "name": "Sky", "capacity": 12},
    ]
