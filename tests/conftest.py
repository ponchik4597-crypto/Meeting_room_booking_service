from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.room.models import Room
from app.slot.models import Slot
from app.user.models import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
AsyncSessionTesting = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True, scope="function")
async def prepare_database():
    """Создаёт таблицы перед каждым тестом, удаляет после."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная сессия БД."""
    async with AsyncSessionTesting() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP клиент с подменой зависимости БД."""

    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def employee_user(db_session):
    from app.auth import password_hash

    user = User(
        login="employee", hashed_password=password_hash.hash("emp"), role="employee"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()


@pytest_asyncio.fixture
async def employee_client(client, employee_user):
    login_data = {"username": "employee", "password": "emp"}
    resp = await client.post("/users/login", data=login_data)
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest_asyncio.fixture
async def admin_user(db_session):
    from app.auth import password_hash

    user = User(
        login="admin", hashed_password=password_hash.hash("adminpass"), role="admin"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()


@pytest_asyncio.fixture
async def admin_client(client, admin_user):
    login_data = {"username": "admin", "password": "adminpass"}
    resp = await client.post("/users/login", data=login_data)
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest_asyncio.fixture
async def test_room(db_session):
    room = Room(name="Test Room", capacity=5)  # без location
    db_session.add(room)
    await db_session.commit()
    await db_session.refresh(room)
    yield room
    await db_session.delete(room)
    await db_session.commit()


@pytest_asyncio.fixture
async def test_slot(db_session, test_room):
    from datetime import time

    slot = Slot(room_id=test_room.id, time_start=time(10, 0), time_end=time(11, 0))
    db_session.add(slot)
    await db_session.commit()
    await db_session.refresh(slot)
    yield slot
    await db_session.delete(slot)
    await db_session.commit()
