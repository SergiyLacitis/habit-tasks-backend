from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends

from habit_tasks.api.v1.auth.dependencies import get_current_admin_user
from habit_tasks.database import AsyncDBSessionDep
from habit_tasks.database.models.user import User
from habit_tasks.schemas.user import UserCreate, UserRead

from .dependencies import create_user_in_db, get_all_users, get_user_by_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
async def get_users(
    admin: Annotated[User, Depends(get_current_admin_user)],
    users: Annotated[Sequence[User], Depends(get_all_users)],
) -> Sequence[User]:
    return users


@router.get("/{id}", response_model=UserRead)
async def get_user(
    admin: Annotated[User, Depends(get_current_admin_user)],
    user: Annotated[User, Depends(get_user_by_id)],
) -> User:
    return user


@router.post("/", response_model=UserRead)
async def create_user(
    admin: Annotated[User, Depends(get_current_admin_user)],
    user_in: UserCreate,
    session: AsyncDBSessionDep,
) -> User:
    return await create_user_in_db(session, user_in)
