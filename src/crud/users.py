from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from schemas.user import UserCreate


async def get(session: AsyncSession, id: int) -> User:
    if user := await session.get(User, id):
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


async def get_all(session: AsyncSession) -> Sequence[User]:
    statement = select(User).order_by(User.id)
    result = await session.scalars(statement=statement)

    return result.all()


async def create(session: AsyncSession, user_create: UserCreate) -> User:
    user = User(**user_create.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
