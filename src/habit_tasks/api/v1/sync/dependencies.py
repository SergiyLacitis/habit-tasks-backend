from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from habit_tasks.database import AsyncDBSessionDep
from habit_tasks.database.models import Task, TaskLog, User
from habit_tasks.schemas.sync import SyncPayload, SyncResponse


async def sync_data_logic(
    session: AsyncDBSessionDep,
    user: User,
    payload: SyncPayload,
) -> SyncResponse:
    tasks_count = 0
    logs_count = 0

    for task_in in payload.created_tasks:
        new_task = Task(**task_in.model_dump(), user_id=user.id)
        session.add(new_task)
        tasks_count += 1

    await session.flush()

    for log_in in payload.new_logs:
        stmt_task = select(Task).where(
            Task.id == log_in.task_id, Task.user_id == user.id
        )
        task = await session.scalar(stmt_task)

        if not task:
            continue

        stmt_log = select(TaskLog).where(
            TaskLog.task_id == log_in.task_id, TaskLog.date == log_in.date
        )
        existing_log = await session.scalar(stmt_log)

        if not existing_log:
            new_log = TaskLog(
                task_id=log_in.task_id, date=log_in.date, status=log_in.status
            )
            session.add(new_log)
            logs_count += 1

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()

    return SyncResponse(processed_tasks=tasks_count, processed_logs=logs_count)
