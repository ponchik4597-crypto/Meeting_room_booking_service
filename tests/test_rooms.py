from datetime import date, timedelta

import pytest

pytestmark = pytest.mark.asyncio


async def test_get_rooms_availability_no_auth(
    client, test_room, test_slot, employee_user, db_session
):
    """Просмотр занятого слота возвращает is_free=False без авторизации"""
    from app.booking.models import Booking

    test_date = date.today() + timedelta(days=1)
    booking = Booking(user_id=employee_user.id, slot_id=test_slot.id, date=test_date)
    db_session.add(booking)
    await db_session.commit()
    response = await client.get("/rooms", params={"date": test_date.isoformat()})
    assert response.status_code == 200
    data = response.json()
    assert data[0]["slots"][0]["is_free"] is False


async def test_get_rooms_availability_free_slot(client, test_room, test_slot):
    """Просмотр свободного слота возвращает is_free=True"""
    test_date = date.today() + timedelta(days=2)
    response = await client.get("/rooms", params={"date": test_date.isoformat()})
    assert response.status_code == 200
    assert response.json()[0]["slots"][0]["is_free"] is True


async def test_get_rooms_empty(client):
    """Запрос списка комнат возвращает пустой список, если комнат нет"""
    response = await client.get("/rooms", params={"date": date.today().isoformat()})
    assert response.status_code == 200
    assert response.json() == []


async def test_create_room_as_admin(admin_client):
    """Создание новой комнаты администратором возвращает 201"""
    payload = {"name": "New Room", "capacity": 20}
    response = await admin_client.post("/rooms", json=payload)
    assert response.status_code == 201


async def test_create_room_duplicate_name_fails(admin_client):
    """Попытка создать комнату с уже существующим названием вызывает 400"""
    await admin_client.post("/rooms", json={"name": "Dupe Room", "capacity": 5})
    response = await admin_client.post(
        "/rooms", json={"name": "Dupe Room", "capacity": 10}
    )
    assert response.status_code == 400


async def test_create_room_as_employee_forbidden(employee_client):
    """Попытка создать комнату обычным сотрудником вызывает 403"""
    response = await employee_client.post(
        "/rooms", json={"name": "Should Fail", "capacity": 2}
    )
    assert response.status_code == 403


async def test_create_room_without_token_fails(client):
    """Попытка создать комнату без JWT-токена вызывает 401"""
    response = await client.post("/rooms", json={"name": "No Token", "capacity": 5})
    assert response.status_code == 401
