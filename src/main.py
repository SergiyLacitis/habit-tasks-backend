from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import api
from config import settings
from database import database_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await database_helper.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router=api.router)


def main():
    uvicorn.run(
        "main:app",
        reload=settings.app.reload,
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    main()
