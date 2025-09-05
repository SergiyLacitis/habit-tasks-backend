from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import IntIDPkMixin


class User(Base, IntIDPkMixin):
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
