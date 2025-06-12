from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Networking(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class Settings(BaseSettings):
    networking: Networking = Networking()


settings = Settings()
