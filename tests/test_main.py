import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_read_root_success(client: AsyncClient):
    """Тест проверки работоспособности корневого эндпоинта"""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Meeting Room Booking API is running",
    }


async def test_register_user_success(client: AsyncClient):
    """Тест успешной регистрации нового сотрудника"""
    payload = {
        "login": "ivan_test",
        "password": "secure_password123",
        "role": "employee",
    }
    response = await client.post("/users/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["login"] == "ivan_test"
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_duplicate_user_fails(client: AsyncClient):
    """Тест блокировки регистрации дубликата пользователя"""
    payload = {
        "login": "duplicate_user",
        "password": "password123",
        "role": "employee",
    }

    await client.post("/users/register", json=payload)
    response = await client.post("/users/register", json=payload)

    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]


async def test_login_success_and_jwt_generation(client: AsyncClient):
    """Тест успешного получения JWT-токена"""
    register_payload = {
        "login": "auth_user",
        "password": "correct_password",
        "role": "employee",
    }
    await client.post("/users/register", json=register_payload)

    login_data = {"username": "auth_user", "password": "correct_password"}
    response = await client.post("/users/login", data=login_data)

    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


async def test_protected_endpoint_without_token_unauthorized(client: AsyncClient):
    """Тест блокировки неавторизованного доступа к бронированиям"""
    payload = {"slot_id": 1, "date": "2026-06-20"}
    response = await client.post("/bookings", json=payload)

    assert response.status_code == 401
