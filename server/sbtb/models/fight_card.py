from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sbtb.core.database.base import RecordModel
from sbtb.models.bout import Bout


class FightCard(RecordModel):
    __tablename__ = "fight_cards"

    event_name: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    network: Mapped[str | None] = mapped_column(String, nullable=True)
    event_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    bouts: Mapped[list["Bout"]] = relationship("Bout", back_populates="fight_card", lazy="selectin")
