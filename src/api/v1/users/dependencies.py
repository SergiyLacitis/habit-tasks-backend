from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.v1.auth import utils
from config import settings
from database import AsyncDBSessionDep
from database.models import User
from schemas.user import UserCreate

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
        payload = utils.decode_token(
            token,
            public_key=settings.auth.public_key_path,
            algorithm=settings.auth.algorithm,
        )
    except InvalidTokenError:
        raise ivalid_token_exeption
    return payload


async def get_current_auth_user(
    payload: Annotated[dict, Depends(get_current_auth_payload)],
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


async def get_user_by_id(session: AsyncDBSessionDep, id: int) -> User:
    if user := await session.get(User, id):
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


async def get_all_users(session: AsyncDBSessionDep) -> Sequence[User]:
    statement = select(User).order_by(User.id)
    result = await session.scalars(statement=statement)

    return result.all()


async def add_user(
    session: AsyncDBSessionDep,
    user_create: UserCreate,
) -> User:
    user = User(**user_create.model_dump())
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with that username or email already exist",
        )
