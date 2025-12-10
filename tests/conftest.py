import asyncio
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from habit_tasks.api.v1.auth.utils import generate_token_info, hash_password
from habit_tasks.database.database_helper import database_helper
from habit_tasks.database.models import Base, User
from habit_tasks.database.models.user import UserRole
from habit_tasks.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    url=TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine_test.sync_engine, "connect")
def enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, autoflush=False, autocommit=False
)


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[database_helper.session_getter] = override_get_db_session


@pytest_asyncio.fixture(scope="session")
async def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clear_data_between_tests(session: AsyncSession):
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_user(session: AsyncSession) -> User:
    user = User(
        username="admin_tester",
        email="admin@test.com",
        password_hash=hash_password("adminpass"),
        role=UserRole.ADMIN,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def regular_user(session: AsyncSession) -> User:
    user = User(
        username="simple_tester",
        email="user@test.com",
        password_hash=hash_password("userpass"),
        role=UserRole.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_client(ac: AsyncClient, admin_user: User) -> AsyncClient:
    token_info = generate_token_info(admin_user)
    ac.headers.update({"Authorization": f"Bearer {token_info.access_token}"})
    return ac


@pytest_asyncio.fixture
async def user_client(ac: AsyncClient, regular_user: User) -> AsyncClient:
    token_info = generate_token_info(regular_user)
    ac.headers.update({"Authorization": f"Bearer {token_info.access_token}"})
    return ac
