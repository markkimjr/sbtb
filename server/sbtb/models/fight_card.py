from datetime import datetime

from sqlalchemy import String, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sbtb.core.database.base import RecordModel


class FightCard(RecordModel):
    __tablename__ = "fight_cards"

    event_name: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    network: Mapped[str | None] = mapped_column(String, nullable=True)
    event_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    bouts: Mapped[list["Bout"]] = relationship("Bout", back_populates="fight_card", lazy="selectin")
