from typing import Annotated

from fastapi import APIRouter, Depends

from habit_tasks.api.v1.users.dependencies import add_user
from habit_tasks.database.models import User
from habit_tasks.schemas.jwt import TokenInfo
from habit_tasks.schemas.user import UserRead

from .dependencies import (
    get_auth_user_from_access_token,
    get_auth_user_from_refresh_token,
    validate_user,
)
from .utils import generate_token_info

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenInfo)
async def login(
    user: Annotated[User, Depends(validate_user)],
):
    return generate_token_info(user)


@router.post("/register", response_model=TokenInfo)
async def register(user: Annotated[User, Depends(add_user)]):
    return generate_token_info(user)


@router.post("/refresh", response_model=TokenInfo)
async def refresh(
    user: Annotated[User, Depends(get_auth_user_from_refresh_token)],
):
    return generate_token_info(user)


@router.get("/users/me", response_model=UserRead)
async def get_me(
    user: Annotated[User, Depends(get_auth_user_from_access_token)],
) -> User:
    return user
