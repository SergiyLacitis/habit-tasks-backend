from collections.abc import Sequence
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from habit_tasks.database import AsyncDBSessionDep
from habit_tasks.database.models import Task, TaskLog, User
from habit_tasks.schemas.task import TaskCreate, TaskUpdate


async def get_user_tasks(
    session: AsyncDBSessionDep,
    user: User,
) -> Sequence[Task]:
    statement = select(Task).where(Task.user_id == user.id).order_by(Task.created_at)
    result = await session.scalars(statement)
    return result.all()


async def get_task_by_id(
    session: AsyncDBSessionDep,
    user: User,
    task_id: int,
) -> Task:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = await session.scalar(statement)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


async def create_task(
    session: AsyncDBSessionDep,
    user: User,
    task_in: TaskCreate,
) -> Task:
    task = Task(**task_in.model_dump(), user_id=user.id)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def update_task_logic(
    session: AsyncDBSessionDep,
    user: User,
    task_id: int,
    task_update: TaskUpdate,
) -> Task:
    task = await get_task_by_id(session, user, task_id)

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task_logic(
    session: AsyncDBSessionDep,
    user: User,
    task_id: int,
) -> None:
    task = await get_task_by_id(session, user, task_id)
    await session.delete(task)
    await session.commit()


async def complete_task_logic(
    session: AsyncDBSessionDep,
    user: User,
    task_id: int,
) -> TaskLog:
    task = await get_task_by_id(session, user, task_id)

    today = date.today()

    stmt_check = select(TaskLog).where(
        TaskLog.task_id == task.id, TaskLog.date == today
    )
    existing_log = await session.scalar(stmt_check)

    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already completed today",
        )

    new_log = TaskLog(task_id=task.id, date=today, status=True)
    session.add(new_log)

    try:
        await session.commit()
        await session.refresh(new_log)
        return new_log
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Could not complete task"
        )
