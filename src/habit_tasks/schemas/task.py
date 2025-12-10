from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    frequency: Optional[str] = Field(default=None, max_length=50)
    reminders: Optional[list[str]] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    frequency: Optional[str] = Field(default=None, max_length=50)
    reminders: Optional[list[str]] = None


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
