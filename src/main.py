from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import settings
from database import database_helper
from routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await database_helper.dispose()


app = FastAPI(lifespan=lifespan)

for router in (users.router, auth.router):
    app.include_router(router)


def main():
    uvicorn.run(
        "main:app",
        reload=settings.app.reload,
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    main()
