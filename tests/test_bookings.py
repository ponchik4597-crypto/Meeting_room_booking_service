from datetime import date, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio


async def test_create_booking_success(employee_client, test_slot):
    """Успешное создание бронирования возвращает 201"""
    booking_date = date.today() + timedelta(days=1)
    payload = {"slot_id": test_slot.id, "date": booking_date.isoformat()}
    response = await employee_client.post("/bookings", json=payload)
    assert response.status_code == 201


async def test_create_booking_past_date_fails(employee_client, test_slot):
    """Попытка забронировать на прошедшую дату вызывает 400"""
    past_date = date.today() - timedelta(days=1)
    payload = {"slot_id": test_slot.id, "date": past_date.isoformat()}
    response = await employee_client.post("/bookings", json=payload)
    assert response.status_code == 400


async def test_create_booking_duplicate_fails(employee_client, test_slot):
    """Повторное бронирование одного и того же слота вызывает 400"""
    booking_date = date.today() + timedelta(days=2)
    payload = {"slot_id": test_slot.id, "date": booking_date.isoformat()}
    await employee_client.post("/bookings", json=payload)
    response = await employee_client.post("/bookings", json=payload)
    assert response.status_code == 400


async def test_create_booking_nonexistent_slot_fails(employee_client):
    """Попытка забронировать несуществующий слот вызывает 404"""
    payload = {"slot_id": 9999, "date": date.today().isoformat()}
    response = await employee_client.post("/bookings", json=payload)
    assert response.status_code == 404


async def test_create_booking_without_token_fails(client, test_slot):
    """Запрос на бронирование без JWT-токена вызывает 401"""
    payload = {"slot_id": test_slot.id, "date": date.today().isoformat()}
    response = await client.post("/bookings", json=payload)
    assert response.status_code == 401


async def test_delete_booking_owner_success(employee_client, test_slot):
    """Удаление своего бронирования владельцем возвращает 204"""
    booking_date = date.today() + timedelta(days=3)
    create_resp = await employee_client.post(
        "/bookings", json={"slot_id": test_slot.id, "date": booking_date.isoformat()}
    )
    booking_id = create_resp.json()["id"]
    del_resp = await employee_client.delete(f"/bookings/{booking_id}")
    assert del_resp.status_code == 204


async def test_delete_booking_admin_success(admin_client, employee_client, test_slot):
    """Удаление любого чужого бронирования администратором возвращает 204"""
    booking_date = date.today() + timedelta(days=4)
    create_resp = await employee_client.post(
        "/bookings", json={"slot_id": test_slot.id, "date": booking_date.isoformat()}
    )
    booking_id = create_resp.json()["id"]
    del_resp = await admin_client.delete(f"/bookings/{booking_id}")
    assert del_resp.status_code == 204


async def test_delete_booking_forbidden_other_user(
    client, test_slot, db_session, employee_client
):
    """Попытка удалить чужое бронирование обычным пользователем вызывает 403"""
    from app.auth import password_hash
    from app.user.models import User

    user2 = User(
        login="otheruser",
        hashed_password=password_hash.hash("otherpass"),
        role="employee",
    )
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    login_resp = await client.post(
        "/users/login", data={"username": "otheruser", "password": "otherpass"}
    )
    assert login_resp.status_code == 200
    token2 = login_resp.json()["access_token"]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client2:
        client2.headers.update({"Authorization": f"Bearer {token2}"})
        booking_date = date.today() + timedelta(days=5)
        create_resp = await client2.post(
            "/bookings",
            json={"slot_id": test_slot.id, "date": booking_date.isoformat()},
        )
        assert create_resp.status_code == 201
        booking_id = create_resp.json()["id"]

        del_resp = await employee_client.delete(f"/bookings/{booking_id}")
        assert del_resp.status_code == 403
        assert "Недостаточно прав для отмены" in del_resp.json()["detail"]

    await db_session.delete(user2)
    await db_session.commit()


async def test_delete_nonexistent_booking_fails(employee_client):
    """Попытка отменить несуществующее бронирование вызывает 404"""
    response = await employee_client.delete("/bookings/99999")
    assert response.status_code == 404


async def test_get_rooms_availability_shows_booking(
    client, test_room, test_slot, employee_user, db_session
):
    """Занятый слот отображается в сетке доступности с флагом is_free=False"""
    from app.booking.models import Booking

    booking_date = date.today() + timedelta(days=1)
    booking = Booking(user_id=employee_user.id, slot_id=test_slot.id, date=booking_date)
    db_session.add(booking)
    await db_session.commit()

    response = await client.get("/rooms", params={"date": booking_date.isoformat()})
    assert response.status_code == 200
    data = response.json()
    room_data = next((r for r in data if r["room_id"] == test_room.id), None)
    assert room_data is not None
    slot_avail = room_data["slots"][0]
    assert slot_avail["is_free"] is False
    assert slot_avail["booking_id"] == booking.id


async def test_get_rooms_availability_free(client, test_room, test_slot):
    """Свободный слот отображается в сетке доступности с флагом is_free=True"""
    free_date = date.today() + timedelta(days=10)
    response = await client.get("/rooms", params={"date": free_date.isoformat()})
    assert response.json()[0]["slots"][0]["is_free"] is True
