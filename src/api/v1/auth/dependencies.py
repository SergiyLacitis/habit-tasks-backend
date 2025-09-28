from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select

from config import settings
from database import AsyncDBSessionDep
from database.models import User

from . import utils

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
ivalid_token_exeption = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid token error",
    headers={"WWW-Authenticate": "Bearer"},
)


async def validate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncDBSessionDep,
) -> User:
    username = form_data.username
    password = form_data.password
    unauthorized_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
    )
    statement = (
        select(User).where(User.email == username)
        if "@" in username
        else select(User).where(User.username == username)
    )
    if not (user := (await session.execute(statement)).scalar_one_or_none()):
        raise unauthorized_exeption

    if utils.validate_password(password=password, hashed_password=user.password):
        return user

    raise unauthorized_exeption


def get_auth_payload(
    token: Annotated[str, Depends(oauth2_bearer)],
) -> dict:
    try:
        payload = utils.decode_token(
            token,
            public_key=settings.auth.public_key_path,
            algorithm=settings.auth.algorithm,
        )
    except InvalidTokenError:
        raise ivalid_token_exeption
    return payload


async def get_auth_user_from_access_token(
    payload: Annotated[dict, Depends(get_auth_payload)],
    session: AsyncDBSessionDep,
) -> User:
    if payload.get("type") == utils.TokenType.ACCESS:
        username: str | None = payload.get("sub")
        statement = select(User).where(User.username == username)
        if user := (await session.execute(statement=statement)).scalar_one_or_none():
            return user

        raise ivalid_token_exeption

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token type"
    )


def get_refresh_token_payload(refresh_token: str) -> dict:
    try:
        payload = utils.decode_token(
            refresh_token,
            public_key=settings.auth.public_key_path,
            algorithm=settings.auth.algorithm,
        )

        if payload.get("type") != utils.TokenType.REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token type - refresh token required",
            )

        return payload

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_auth_user_from_refresh_token(
    refresh_token: Annotated[str, Depends(get_refresh_token_payload)],
    session: AsyncDBSessionDep,
) -> User:
    payload = get_refresh_token_payload(refresh_token)
    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token payload"
        )

    statement = select(User).where(User.username == username)
    user = (await session.execute(statement)).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
        )

    return user
