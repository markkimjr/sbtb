from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from sbtb.core.database.base import RecordModel


class CombatSport(StrEnum):
    boxing = "boxing"
    mma = "mma"


class FightOrganization(RecordModel):
    __tablename__ = "fight_organizations"

    name: Mapped[str] = mapped_column(String, nullable=False)
    sport: Mapped[CombatSport | None] = mapped_column(
        ENUM(CombatSport, name="combatsport", create_type=True), nullable=True
    )

    __table_args__ = (UniqueConstraint("name", name="uq_fight_organizations_name"),)
