from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from crud import UsersCRUD
from database import database_helper
from database.models.user import User
from schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
async def get_users(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
) -> Sequence[User]:
    users = await UsersCRUD.get_all(session=session)
    return users


@router.get("/{id}", response_model=UserRead)
async def get_user(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)], id: int
) -> User:
    user = await UsersCRUD.get(session=session, id=id)
    return user


@router.post("/", response_model=UserRead)
async def create_user(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    user_create: UserCreate,
) -> User:
    user = await UsersCRUD.create(session=session, user_create=user_create)
    return user
