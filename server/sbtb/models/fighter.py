from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from sbtb.core.database.base import RecordModel


class Fighter(RecordModel):
    __tablename__ = "fighters"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    wins: Mapped[int] = mapped_column(nullable=False, default=0)
    losses: Mapped[int] = mapped_column(nullable=False, default=0)
    draws: Mapped[int] = mapped_column(nullable=False, default=0)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
