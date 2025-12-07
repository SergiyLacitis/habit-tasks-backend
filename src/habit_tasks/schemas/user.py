from pydantic import BaseModel, ConfigDict, EmailStr

from habit_tasks.database.models.user import UserRole


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
