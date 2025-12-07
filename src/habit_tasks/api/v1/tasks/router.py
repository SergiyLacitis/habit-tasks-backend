from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from habit_tasks.api.v1.auth.dependencies import get_auth_user_from_access_token
from habit_tasks.database import AsyncDBSessionDep
from habit_tasks.database.models import User
from habit_tasks.schemas.task import (
    TaskCreate,
    TaskLogResponse,
    TaskResponse,
    TaskUpdate,
)

from .dependencies import (
    complete_task_logic,
    create_task,
    delete_task_logic,
    get_task_by_id,
    get_task_logs_logic,
    get_user_tasks,
    undo_complete_task_logic,
    update_task_logic,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

CurrentUser = Annotated[User, Depends(get_auth_user_from_access_token)]


@router.get("/", response_model=list[TaskResponse])
async def get_my_tasks(
    session: AsyncDBSessionDep,
    user: CurrentUser,
):
    return await get_user_tasks(session, user)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    session: AsyncDBSessionDep,
    user: CurrentUser,
    task_in: TaskCreate,
):
    return await create_task(session, user, task_in)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: AsyncDBSessionDep,
    user: CurrentUser,
):
    return await get_task_by_id(session, user, task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncDBSessionDep,
    user: CurrentUser,
):
    return await update_task_logic(session, user, task_id, task_update)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: AsyncDBSessionDep,
    user: CurrentUser,
):
    await delete_task_logic(session, user, task_id)


@router.get("/{task_id}/logs", response_model=list[TaskLogResponse])
async def get_task_history(
    task_id: int,
    session: AsyncDBSessionDep,
    user: CurrentUser,
    date_from: Annotated[date | None, Query(description="Start date filter")] = None,
    date_to: Annotated[date | None, Query(description="End date filter")] = None,
):
    return await get_task_logs_logic(session, user, task_id, date_from, date_to)


@router.post("/{task_id}/complete", response_model=TaskLogResponse)
async def complete_task(
    task_id: int,
    session: AsyncDBSessionDep,
    user: CurrentUser,
):
    return await complete_task_logic(session, user, task_id)


@router.delete("/{task_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def undo_complete_task(
    task_id: int,
    session: AsyncDBSessionDep,
    user: CurrentUser,
    date: Annotated[
        date | None, Query(description="Date to undo (defaults to today)")
    ] = None,
):
    await undo_complete_task_logic(session, user, task_id, date)
