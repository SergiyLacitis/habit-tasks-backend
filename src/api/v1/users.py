from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import utils
from config import settings
from database import database_helper
from database.models.user import User
from schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

ivalid_token_exeption = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid token error",
    headers={"WWW-Authenticate": "Bearer"},
)


@router.get("/", response_model=list[UserRead])
async def get_users(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
) -> Sequence[User]:
    users = await crud.users.get_all(session=session)
    return users


@router.post("/", response_model=UserRead)
async def create_user(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
    user_create: UserCreate,
) -> User:
    user = await crud.users.create(session=session, user_create=user_create)
    return user


def get_current_auth_payload(
    token: Annotated[str, Depends(oauth2_bearer)],
) -> dict:
    try:
        payload = utils.auth.decode_token(
            token,
            public_key=settings.auth.public_key_path,
            algorithm=settings.auth.algorithm,
        )
    except InvalidTokenError:
        raise ivalid_token_exeption
    return payload


async def get_current_auth_user(
    payload: Annotated[dict, Depends(get_current_auth_payload)],
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
) -> User:
    username: str | None = payload.get("sub")
    statement = select(User).where(User.username == username)
    if user := (await session.execute(statement=statement)).scalar_one_or_none():
        return user

    raise ivalid_token_exeption


@router.get("/me", response_model=UserRead)
async def get_me(user: Annotated[User, Depends(get_current_auth_user)]) -> User:
    return user
