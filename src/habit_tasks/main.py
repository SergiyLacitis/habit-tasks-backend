from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from habit_tasks import api
from habit_tasks.config import settings
from habit_tasks.database import database_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await database_helper.dispose()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=api.router)


def main():
    uvicorn.run(
        "habit_tasks.main:app",
        reload=settings.app.reload,
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    main()
