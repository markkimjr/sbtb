from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from sbtb.core.database.base import RecordModel


class Fighter(RecordModel):
    __tablename__ = "fighters"

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    nickname: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    wins: Mapped[int | None] = mapped_column(nullable=True, default=0)
    losses: Mapped[int | None] = mapped_column(nullable=True, default=0)
    draws: Mapped[int | None] = mapped_column(nullable=True, default=0)
