from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class User(Base):
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
