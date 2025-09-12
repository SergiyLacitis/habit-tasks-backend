from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import utils
from config import settings
from database import database_helper
from database.models import User

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


ivalid_token_exeption = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid token error",
    headers={"WWW-Authenticate": "Bearer"},
)


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
