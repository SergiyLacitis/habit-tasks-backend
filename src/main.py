import uvicorn
from fastapi import FastAPI

from config import settings
from routers import users

app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["Users"])


def main():
    uvicorn.run(
        "main:app",
        reload=settings.app.reload,
        host=settings.app.host,
        port=settings.app.port,
    )


if __name__ == "__main__":
    main()
