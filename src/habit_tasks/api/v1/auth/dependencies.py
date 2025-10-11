from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select

from habit_tasks.config import settings
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


def decode_token_payload(token: str) -> dict:
    """Decode JWT token and return payload."""
    try:
        return utils.decode_token(
            token,
            public_key=settings.auth.public_key_path,
            algorithm=settings.auth.algorithm,
        )
    except InvalidTokenError:
        raise INVALID_TOKEN_EXCEPTION


def validate_token_type(payload: dict, expected_type: utils.TokenType) -> dict:
    """Validate token type."""
    if payload.get("type") != expected_type:
        raise INVALID_TOKEN_TYPE_EXCEPTION
    return payload


async def get_user_by_identifier(
    session: AsyncDBSessionDep, identifier: str, field: str = "username"
) -> User | None:
    """Get user by identifier (username or email)."""
    if field == "auto":
        field = "email" if "@" in identifier else "username"

    statement = select(User).where(getattr(User, field) == identifier)
    return (await session.execute(statement)).scalar_one_or_none()


def extract_username_from_payload(payload: dict) -> str:
    """Extract username from token payload."""
    username = payload.get("sub")
    if not username:
        raise INVALID_TOKEN_EXCEPTION
    return username


async def validate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncDBSessionDep,
) -> User:
    """Validate user credentials during login."""
    user = await get_user_by_identifier(session, form_data.username, "auto")

    if not user:
        raise INVALID_CREDENTIALS_EXCEPTION

    if not utils.validate_password(
        password=form_data.password, hashed_password=user.password
    ):
        raise INVALID_CREDENTIALS_EXCEPTION

    return user


def get_auth_payload(
    token: Annotated[str, Depends(oauth2_bearer)],
) -> dict:
    """Decode and validate JWT token payload."""
    return decode_token_payload(token)


async def get_user_from_token_payload(
    payload: dict, session: AsyncDBSessionDep, expected_token_type: utils.TokenType
) -> User:
    """Common logic for getting user from token payload."""
    validate_token_type(payload, expected_token_type)
    username = extract_username_from_payload(payload)

    user = await get_user_by_identifier(session, username, "username")
    if not user:
        raise USER_NOT_FOUND_EXCEPTION

    return user


async def get_auth_user_from_access_token(
    payload: Annotated[dict, Depends(get_auth_payload)],
    session: AsyncDBSessionDep,
) -> User:
    """Get authenticated user from access token."""
    return await get_user_from_token_payload(payload, session, utils.TokenType.ACCESS)


def get_refresh_token_payload(refresh_token: str) -> dict:
    """Decode and validate refresh token payload."""
    payload = decode_token_payload(refresh_token)
    return validate_token_type(payload, utils.TokenType.REFRESH)


async def get_auth_user_from_refresh_token(
    payload: Annotated[dict, Depends(get_refresh_token_payload)],
    session: AsyncDBSessionDep,
) -> User:
    """Get authenticated user from refresh token."""
    return await get_user_from_token_payload(payload, session, utils.TokenType.REFRESH)
