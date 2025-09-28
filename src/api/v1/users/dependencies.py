from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import AsyncDBSessionDep
from database.models import User
from schemas.user import UserCreate


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
