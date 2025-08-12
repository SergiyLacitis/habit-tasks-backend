from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
