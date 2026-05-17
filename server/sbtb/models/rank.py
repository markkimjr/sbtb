from uuid import UUID

from sqlalchemy import ForeignKey, Double
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from sbtb.core.database.base import RecordModel


class Rank(RecordModel):
    __tablename__ = "ranks"

    rank: Mapped[float] = mapped_column(Double, nullable=False)
    fighter_id: Mapped[UUID] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    weight_class_id: Mapped[UUID] = mapped_column(ForeignKey("weight_classes.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("fight_organizations.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("rank", "weight_class_id", "organization_id"),
    )
