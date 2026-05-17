from enum import Enum

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from sbtb.core.database.base import RecordModel


class FightOrganization(RecordModel):
    __tablename__ = "fight_organizations"

    class FightOrganizationEnum(Enum):
        UFC = "UFC"
        WBO = "WBO"
        WBC = "WBC"
        IBF = "IBF"
        WBA = "WBA"

    name: Mapped[str | None] = mapped_column(ENUM(FightOrganizationEnum), nullable=True)
