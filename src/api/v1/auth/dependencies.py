from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from database import AsyncDBSessionDep
from database.models import User

from . import utils


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
