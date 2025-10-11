from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import IntIDPkMixin


class Event(Base, IntIDPkMixin):
    date: Mapped[str]
    title: Mapped[str]

    friend_id: Mapped[int] = mapped_column(ForeignKey("friends.id"))
