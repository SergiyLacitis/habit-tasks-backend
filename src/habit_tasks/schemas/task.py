from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    reminders: list[str] | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    reminders: list[str] | None = None


class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class TaskLogResponse(BaseModel):
    id: int
    task_id: int
    date: datetime
    status: bool

    model_config = ConfigDict(from_attributes=True)
