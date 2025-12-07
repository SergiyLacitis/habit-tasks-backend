from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select

from habit_tasks.database import AsyncDBSessionDep
from habit_tasks.database.models import User

from . import utils
from .exceptions import (
    INVALID_CREDENTIALS_EXCEPTION,
    INVALID_TOKEN_EXCEPTION,
    INVALID_TOKEN_TYPE_EXCEPTION,
    USER_NOT_FOUND_EXCEPTION,
)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def validate_user(
    session: AsyncDBSessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> User:
    stmt = select(User).where(
        (User.username == form_data.username) | (User.email == form_data.username)
    )
    user = (await session.execute(stmt)).scalar_one_or_none()

    if not user:
        raise INVALID_CREDENTIALS_EXCEPTION

    if not utils.validate_password(form_data.password, user.password_hash):
        raise INVALID_CREDENTIALS_EXCEPTION

    return user


async def get_current_user_payload(
    token: Annotated[str, Depends(oauth2_bearer)],
) -> dict:
    try:
        return utils.decode_token(token)
    except InvalidTokenError:
        raise INVALID_TOKEN_EXCEPTION


async def get_auth_user_from_token(
    payload: dict,
    session: AsyncDBSessionDep,
    expected_type: utils.TokenType,
) -> User:
    token_type = payload.get("type")
    if token_type != expected_type:
        raise INVALID_TOKEN_TYPE_EXCEPTION

    username = payload.get("sub")
    if not username:
        raise INVALID_TOKEN_EXCEPTION

    stmt = select(User).where(User.username == username)
    user = (await session.execute(stmt)).scalar_one_or_none()

    if not user:
        raise USER_NOT_FOUND_EXCEPTION

    return user


async def get_auth_user_from_access_token(
    payload: Annotated[dict, Depends(get_current_user_payload)],
    session: AsyncDBSessionDep,
) -> User:
    return await get_auth_user_from_token(payload, session, utils.TokenType.ACCESS)


async def get_auth_user_from_refresh_token(
    payload: Annotated[dict, Depends(get_current_user_payload)],
    session: AsyncDBSessionDep,
) -> User:
    return await get_auth_user_from_token(payload, session, utils.TokenType.REFRESH)
