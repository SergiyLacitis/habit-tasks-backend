from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter

from database.models.user import User
from schemas.user import UserRead

from .dependencies import add_user, get_all_users, get_current_auth_user, get_user_by_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
async def get_users(
    users: Annotated[Sequence[User], Depends(get_all_users)],
) -> Sequence[User]:
    return users


@router.get("/{id}", response_model=UserRead)
async def get_user(
    user: Annotated[User, Depends(get_user_by_id)],
) -> User:
    return user


@router.post("/", response_model=UserRead)
async def create_user(
    user: Annotated[User, Depends(add_user)],
) -> User:
    return user


@router.get("/me", response_model=UserRead)
async def get_me(user: Annotated[User, Depends(get_current_auth_user)]) -> User:
    return user
