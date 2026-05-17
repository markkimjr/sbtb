from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sbtb.core.database.base import RecordModel

if TYPE_CHECKING:
    from sbtb.models import FightCard, Fighter


class Bout(RecordModel):
    __tablename__ = "bouts"

    fight_card_id: Mapped[UUID] = mapped_column(ForeignKey("fight_cards.id"), nullable=False)
    red_corner_id: Mapped[UUID] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    blue_corner_id: Mapped[UUID] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    bout_order: Mapped[int | None] = mapped_column(nullable=True)
    is_title_fight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    fight_card: Mapped["FightCard"] = relationship("FightCard", back_populates="bouts")
    red_corner: Mapped["Fighter"] = relationship("Fighter", foreign_keys=[red_corner_id], lazy="joined")
    blue_corner: Mapped["Fighter"] = relationship("Fighter", foreign_keys=[blue_corner_id], lazy="joined")
