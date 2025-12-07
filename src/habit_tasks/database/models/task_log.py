from __future__ import annotations

from datetime import date as DateType

from sqlalchemy import Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IntIDPkMixin


class TaskLog(Base, IntIDPkMixin):
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    date: Mapped[DateType] = mapped_column(Date, default=DateType.today, index=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    task: Mapped["Task"] = relationship("Task", back_populates="logs")
    __table_args__ = (UniqueConstraint("task_id", "date", name="uq_task_log_date"),)
