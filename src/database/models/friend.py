from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Friend(Base):
    name: Mapped[str]
    birdthDay: Mapped[str]
    is_favority: Mapped[bool] = mapped_column(default=False)
    color: Mapped[str]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
