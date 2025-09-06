from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import utils
from config import settings
from database import database_helper
from database.models import User
from schemas.jwt import TokenInfo
from schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])

unauthorized_exeption = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
)

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

ivalid_token_exeption = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid token error",
    headers={"WWW-Authenticate": "Bearer"},
)


async def validate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
) -> User:
    username = form_data.username
    password = form_data.password
    statement = (
        select(User).where(User.email == username)
        if "@" in username
        else select(User).where(User.username == username)
    )
    if not (user := (await session.execute(statement)).scalar_one_or_none()):
        raise unauthorized_exeption

    if utils.auth.validate_password(password=password, hashed_password=user.password):
        return user

    raise unauthorized_exeption


@router.post("/login", response_model=TokenInfo)
async def login(
    user: Annotated[User, Depends(validate_user)],
):
    payload = {"sub": user.username}

    token = utils.auth.encode_token(
        payload=payload,
        private_key=settings.auth.secret_key_path,
        algorithm=settings.auth.algorithm,
        expire_minutes=settings.auth.access_token_expire_minutes,
    )
    return TokenInfo(access_token=token, token_type="Bearer")


@router.post("/register")
async def register(
    session: Annotated[AsyncSession, Depends(database_helper.session_getter)],
): ...


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
