from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict, EmailStr, field_serializer

from habit_tasks.api.v1.auth.utils import hash_password


class UserLogin(BaseModel):
    model_config = ConfigDict(strict=True)
    email: EmailStr | None = None
    username: Annotated[str, MinLen(3), MaxLen(20)] | None = None
    password: bytes


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str

    @field_serializer("password")
    def serialize_password(self, password: str) -> bytes:
        return hash_password(password=password)


class UserRead(UserBase):
    id: int

    ConfigDict(from_attributes=True)
