import uvicorn
from fastapi import FastAPI

from config import settings
from routers import users

app = FastAPI()
app.include_router(users.router, prefix="/users", tags=["Users"])


def main():
    uvicorn.run(
        "main:app",
        host=settings.networking.host,
        port=settings.networking.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )


if __name__ == "__main__":
    main()
