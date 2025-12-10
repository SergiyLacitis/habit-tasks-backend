import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from habit_tasks.database.models import User

pytestmark = pytest.mark.asyncio


async def test_create_user_by_admin(admin_client: AsyncClient, session: AsyncSession):
    payload = {
        "username": "new_user",
        "email": "new@example.com",
        "password": "strongpassword123",
    }

    response = await admin_client.post("/api/v1/users/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["role"] == "user"
    assert "id" in data

    stmt = select(User).where(User.email == payload["email"])
    user_in_db = await session.scalar(stmt)
    assert user_in_db is not None
    assert user_in_db.username == payload["username"]


async def test_create_user_duplicate_email(
    admin_client: AsyncClient, regular_user: User
):
    payload = {
        "username": "another_name",
        "email": regular_user.email,
        "password": "pass",
    }

    response = await admin_client.post("/api/v1/users/", json=payload)
    assert response.status_code == 409


async def test_get_users_list_by_admin(
    admin_client: AsyncClient, admin_user: User, regular_user: User
):
    response = await admin_client.get("/api/v1/users/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    ids = [u["id"] for u in data]
    assert admin_user.id in ids
    assert regular_user.id in ids


async def test_get_user_by_id_admin(admin_client: AsyncClient, regular_user: User):
    response = await admin_client.get(f"/api/v1/users/{regular_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == regular_user.id
    assert data["email"] == regular_user.email


async def test_get_user_not_found(admin_client: AsyncClient):
    response = await admin_client.get("/api/v1/users/999999")
    assert response.status_code == 404


async def test_regular_user_cannot_create_user(user_client: AsyncClient):
    payload = {"username": "hacker", "email": "hacker@example.com", "password": "pass"}
    response = await user_client.post("/api/v1/users/", json=payload)
    assert response.status_code == 403


async def test_regular_user_cannot_get_users_list(user_client: AsyncClient):
    response = await user_client.get("/api/v1/users/")
    assert response.status_code == 403


async def test_regular_user_cannot_get_user_by_id(
    user_client: AsyncClient, admin_user: User
):
    response = await user_client.get(f"/api/v1/users/{admin_user.id}")
    assert response.status_code == 403


async def test_unauthenticated_access(ac: AsyncClient):
    response = await ac.get("/api/v1/users/")
    assert response.status_code == 401
