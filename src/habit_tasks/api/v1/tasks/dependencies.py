from collections.abc import Sequence
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError

from habit_tasks.database import AsyncDBSessionDep
from habit_tasks.database.models import Task, TaskLog, User
from habit_tasks.schemas.task import TaskCreate, TaskResponse, TaskUpdate


async def get_user_tasks(
    session: AsyncDBSessionDep,
    user: User,
) -> Sequence[TaskResponse]:
    today = date.today()

    stmt = (
        select(Task, TaskLog.id)
        .outerjoin(TaskLog, and_(Task.id == TaskLog.task_id, TaskLog.date == today))
        .where(Task.user_id == user.id)
        .order_by(Task.created_at)
    )

    result = await session.execute(stmt)

    tasks_with_status = []
    for task, log_id in result:
        task_dto = TaskResponse.model_validate(task)
        task_dto.is_completed = log_id is not None
        tasks_with_status.append(task_dto)

    return tasks_with_status


async def get_task_by_id(
    session: AsyncDBSessionDep,
    user: User,
    task_id: int,
) -> Task:
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user.id)
    task = await session.scalar(stmt)
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


async def get_task_logs_logic(
    session: AsyncDBSessionDep,
    user: User,
    task_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Sequence[TaskLog]:
    await get_task_by_id(session, user, task_id)

    stmt = (
        select(TaskLog).where(TaskLog.task_id == task_id).order_by(TaskLog.date.desc())
    )

    if date_from:
        stmt = stmt.where(TaskLog.date >= date_from)
    if date_to:
        stmt = stmt.where(TaskLog.date <= date_to)

    result = await session.scalars(stmt)
    return result.all()


async def undo_complete_task_logic(
    session: AsyncDBSessionDep,
    user: User,
    task_id: int,
    target_date: date | None = None,
) -> None:
    task = await get_task_by_id(session, user, task_id)

    if target_date is None:
        target_date = date.today()

    # 2. Шукаємо лог
    stmt = select(TaskLog).where(
        TaskLog.task_id == task.id, TaskLog.date == target_date
    )
    log_entry = await session.scalar(stmt)

    if not log_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task was not completed on {target_date}",
        )

    # 3. Видаляємо
    await session.delete(log_entry)
    await session.commit()
