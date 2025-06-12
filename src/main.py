import uvicorn

from config import settings


def main():
    uvicorn.run(
        "src.main:app",
        host=settings.networking.host,
        port=settings.networking.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
