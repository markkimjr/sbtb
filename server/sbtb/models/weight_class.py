from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from sbtb.core.database.base import RecordModel
from sbtb.models.fight_organization import CombatSport


class WeightClass(RecordModel):
    __tablename__ = "weight_classes"

    name: Mapped[str] = mapped_column(String, nullable=False)
    pounds: Mapped[int | None] = mapped_column(nullable=True)
    sport: Mapped[CombatSport] = mapped_column(ENUM(CombatSport, name="combatsport", create_type=False), nullable=False)

    __table_args__ = (UniqueConstraint("name", "sport", name="uq_weight_classes_name_sport"),)
