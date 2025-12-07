from datetime import date
from typing import List

from pydantic import BaseModel

from habit_tasks.schemas.task import TaskCreate


class TaskLogSync(BaseModel):
    task_id: int
    date: date
    status: bool


class SyncPayload(BaseModel):
    created_tasks: List[TaskCreate] = []
    new_logs: List[TaskLogSync] = []


class SyncResponse(BaseModel):
    processed_tasks: int
    processed_logs: int
    status: str = "ok"
