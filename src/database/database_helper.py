from typing import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool,
        echo_pool: bool,
        pool_size: int,
        max_overflow: int,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


url = URL.create(
    drivername=f"{settings.database.engine.name}+asyncpg",
    username=settings.database.user,
    password=settings.database.password,
    host=settings.database.host,
    port=settings.database.port,
    database=settings.database.name,
).render_as_string(hide_password=False)

database_helper = DatabaseHelper(
    url=url,
    echo=settings.database.engine.echo,
    echo_pool=settings.database.engine.echo_pool,
    pool_size=settings.database.engine.pool_size,
    max_overflow=settings.database.engine.max_overflow,
)
