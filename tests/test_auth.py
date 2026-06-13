from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth import create_access_token, get_current_user
from app.config import settings
from app.user.models import User

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def registered_user(db_session):
    """Создаёт реального пользователя в БД и возвращает его данные"""
    from app.auth import password_hash

    login = "testuser"
    password = "testpass"
    hashed = password_hash.hash(password)

    user = User(login=login, hashed_password=hashed, role="employee")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    yield {"id": user.id, "login": login, "password": password}

    await db_session.delete(user)
    await db_session.commit()


async def test_create_access_token_returns_jwt():
    """Функция create_access_token возвращает валидный JWT"""
    payload = {"sub": "alice"}
    token = create_access_token(payload)

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "alice"
    assert "exp" in decoded
    exp_timestamp = decoded["exp"]
    expected_exp = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    assert abs(exp_timestamp - int(expected_exp.timestamp())) <= 1


async def test_get_current_user_valid_token(db_session, registered_user):
    """Передан валидный токен, возвращается объект User"""
    token = create_access_token({"sub": registered_user["login"]})
    user = await get_current_user(token, session=db_session)
    assert user.id == registered_user["id"]
    assert user.login == registered_user["login"]


async def test_get_current_user_invalid_token(db_session):
    """Неверный токен вызывает 401"""
    with pytest.raises(Exception) as exc_info:
        await get_current_user("not.a.jwt", session=db_session)

    from fastapi import HTTPException

    assert isinstance(exc_info.value, HTTPException)
    assert exc_info.value.status_code == 401


async def test_get_current_user_expired_token(db_session, registered_user):
    """Токен с истекшим сроком жизни вызывает 401"""

    payload = {"sub": registered_user["login"]}
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode = payload.copy()
    to_encode.update({"exp": expire})
    expired_token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    with pytest.raises(Exception) as exc_info:
        await get_current_user(expired_token, session=db_session)
    from fastapi import HTTPException

    assert isinstance(exc_info.value, HTTPException)
    assert exc_info.value.status_code == 401


async def test_get_current_user_missing_sub_claim(db_session):
    """Токен без поля 'sub' вызывает 401"""
    payload = {"something": "else"}
    token = create_access_token(payload)
    with pytest.raises(Exception) as exc_info:
        await get_current_user(token, session=db_session)
    from fastapi import HTTPException

    assert isinstance(exc_info.value, HTTPException)
    assert exc_info.value.status_code == 401


async def test_get_current_user_user_not_found(db_session):
    """Токен с sub, указывающим на несуществующего пользователя, вызывает 401"""
    token = create_access_token({"sub": "nobody"})
    with pytest.raises(Exception) as exc_info:
        await get_current_user(token, session=db_session)
    from fastapi import HTTPException

    assert isinstance(exc_info.value, HTTPException)
    assert exc_info.value.status_code == 401


async def test_get_current_user_token_wrong_secret(db_session, registered_user):
    """Токен, подписанный другим секретом, вызывает 401"""
    wrong_secret = "wrong_very_secret_key_1234567890"
    payload = {"sub": registered_user["login"]}
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = payload.copy()
    to_encode.update({"exp": expire})
    fake_token = jwt.encode(to_encode, wrong_secret, algorithm=settings.ALGORITHM)

    with pytest.raises(Exception) as exc_info:
        await get_current_user(fake_token, session=db_session)
    from fastapi import HTTPException

    assert isinstance(exc_info.value, HTTPException)
    assert exc_info.value.status_code == 401
