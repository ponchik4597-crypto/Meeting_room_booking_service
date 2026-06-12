import pytest

pytestmark = pytest.mark.asyncio


async def test_register_user_success(client):
    """Успешная регистрация нового пользователя возвращает 201"""
    payload = {"login": "reg_success", "password": "password123", "role": "employee"}
    response = await client.post("/users/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["login"] == "reg_success"


async def test_register_user_duplicate_fails(client):
    """Попытка зарегистрировать пользователя с уже существующим логином вызывает 400"""
    login = "duplicate_user"
    payload = {"login": login, "password": "password123", "role": "employee"}
    resp1 = await client.post("/users/register", json=payload)
    assert resp1.status_code == 201, f"First registration failed: {resp1.text}"
    resp2 = await client.post("/users/register", json=payload)
    assert resp2.status_code == 400
    assert "уже существует" in resp2.json()["detail"]


async def test_register_user_case_insensitive_duplicate(client):
    """Регистрация дубликата логина в другом регистре вызывает 400"""
    await client.post(
        "/users/register",
        json={"login": "UniqueCase", "password": "password1", "role": "employee"},
    )
    response = await client.post(
        "/users/register",
        json={"login": "uniquecase", "password": "password2", "role": "employee"},
    )
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]


async def test_register_user_invalid_role(client):
    """Попытка зарегистрировать пользователя с недопустимой ролью вызывает 422"""
    payload = {"login": "badrole", "password": "password123", "role": "superuser"}
    response = await client.post("/users/register", json=payload)
    assert response.status_code == 422


async def test_login_success(client):
    """Успешный вход пользователя возвращает JWT-токен и код 200"""
    await client.post(
        "/users/register",
        json={"login": "logmein", "password": "secret123", "role": "employee"},
    )
    login_data = {"username": "logmein", "password": "secret123"}
    response = await client.post("/users/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(client):
    """Попытка входа с неверным паролем вызывает 401"""
    await client.post(
        "/users/register",
        json={"login": "wrongpass", "password": "correct123", "role": "employee"},
    )
    response = await client.post(
        "/users/login", data={"username": "wrongpass", "password": "wrong"}
    )
    assert response.status_code == 401


async def test_login_nonexistent_user(client):
    """Попытка входа под несуществующим пользователем вызывает 401"""
    response = await client.post(
        "/users/login", data={"username": "ghost", "password": "any"}
    )
    assert response.status_code == 401


async def test_login_case_insensitive(client):
    """Успешный вход по логину в любом регистре возвращает JWT-токен и код 200"""
    await client.post(
        "/users/register",
        json={"login": "CaseLogin", "password": "pass1234", "role": "employee"},
    )
    response = await client.post(
        "/users/login", data={"username": "caselogin", "password": "pass1234"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
