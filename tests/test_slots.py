from datetime import time

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_slot_as_admin(admin_client, test_room):
    """Создание нового временного слота администратором возвращает 201"""
    payload = {"room_id": test_room.id, "time_start": "14:00", "time_end": "15:00"}
    response = await admin_client.post("/slots", json=payload)
    assert response.status_code == 201


async def test_create_slot_overlap_fails(admin_client, test_room, db_session):
    """Попытка создать пересекающийся по времени слот в одной комнате вызывает 400"""
    from app.slot.models import Slot

    slot1 = Slot(room_id=test_room.id, time_start=time(10, 0), time_end=time(11, 0))
    db_session.add(slot1)
    await db_session.commit()
    payload = {"room_id": test_room.id, "time_start": "10:30", "time_end": "11:30"}
    response = await admin_client.post("/slots", json=payload)
    assert response.status_code == 400


async def test_create_slot_invalid_time_range(admin_client, test_room):
    """Если время начала слота больше времени его окончания, возвращается 400"""
    payload = {"room_id": test_room.id, "time_start": "15:00", "time_end": "14:00"}
    response = await admin_client.post("/slots", json=payload)
    assert response.status_code == 400


async def test_create_slot_nonexistent_room(admin_client):
    """Попытка привязать слот к несуществующей переговорной комнате вызывает 404"""
    payload = {"room_id": 9999, "time_start": "09:00", "time_end": "10:00"}
    response = await admin_client.post("/slots", json=payload)
    assert response.status_code == 404


async def test_create_slot_as_employee_forbidden(employee_client, test_room):
    """Попытка создать временной слот обычным сотрудником вызывает 403"""
    payload = {"room_id": test_room.id, "time_start": "12:00", "time_end": "13:00"}
    response = await employee_client.post("/slots", json=payload)
    assert response.status_code == 403


async def test_create_slot_without_token_fails(client, test_room):
    """Создание временного слота без передачи JWT-токена доступа вызывает 401"""
    payload = {"room_id": test_room.id, "time_start": "08:00", "time_end": "09:00"}
    response = await client.post("/slots", json=payload)
    assert response.status_code == 401