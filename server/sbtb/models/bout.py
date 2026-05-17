from uuid import UUID

from sqlalchemy import ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from sbtb.core.database.base import RecordModel


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
