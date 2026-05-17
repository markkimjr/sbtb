from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Integer, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint

from sbtb.core.database.base import RecordModel

if TYPE_CHECKING:
    from sbtb.models import Fighter, FightOrganization, WeightClass


class RankType(StrEnum):
    champion = "champion"
    interim_champion = "interim_champion"
    champion_in_recess = "champion_in_recess"
    contender = "contender"


class Rank(RecordModel):
    __tablename__ = "ranks"

    fighter_id: Mapped[UUID] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    weight_class_id: Mapped[UUID] = mapped_column(ForeignKey("weight_classes.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("fight_organizations.id"), nullable=False)
    rank_type: Mapped[RankType] = mapped_column(ENUM(RankType, name="ranktype", create_type=True), nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1–15 for contenders, NULL for champion types

    fighter: Mapped["Fighter"] = relationship("Fighter")
    weight_class: Mapped["WeightClass"] = relationship("WeightClass")
    organization: Mapped["FightOrganization"] = relationship("FightOrganization")

    __table_args__ = (
        # One fighter per contender position per org/weight class
        UniqueConstraint("weight_class_id", "organization_id", "position", name="uq_rank_contender_position"),
        # One champion type per org/weight class — partial index excludes contenders,
        # since multiple contenders share the same rank_type distinguished only by position
        Index(
            "uq_rank_champion_type",
            "weight_class_id",
            "organization_id",
            "rank_type",
            unique=True,
            postgresql_where=text("rank_type != 'contender'"),
        ),
    )
