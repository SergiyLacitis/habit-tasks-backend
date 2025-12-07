from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from habit_tasks.api.v1.auth.utils import hash_password
from habit_tasks.database import AsyncDBSessionDep
from habit_tasks.database.models import User
from habit_tasks.schemas.user import UserCreate


async def get_user_by_id(session: AsyncDBSessionDep, id: int) -> User:
    if user := await session.get(User, id):
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


async def get_all_users(session: AsyncDBSessionDep) -> Sequence[User]:
    statement = select(User).order_by(User.id)
    result = await session.scalars(statement=statement)
    return result.all()


async def create_user_in_db(
    session: AsyncDBSessionDep,
    user_create: UserCreate,
) -> User:
    hashed_pwd = hash_password(user_create.password)
    user_data = user_create.model_dump(exclude={"password"})
    user_data["password_hash"] = hashed_pwd

    user = User(**user_data)
    session.add(user)

    try:
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with that username or email already exists",
        )


async def add_user(
    session: AsyncDBSessionDep,
    user_create: UserCreate,
) -> User:
    return await create_user_in_db(session, user_create)
