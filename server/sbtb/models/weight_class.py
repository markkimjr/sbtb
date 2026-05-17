from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from sbtb.core.database.base import RecordModel


class WeightClass(RecordModel):
    __tablename__ = "weight_classes"

    name: Mapped[str] = mapped_column(String, nullable=False)
    pounds: Mapped[int | None] = mapped_column(nullable=True)
    kilos: Mapped[int | None] = mapped_column(nullable=True)
    upper_limit: Mapped[int | None] = mapped_column(nullable=True)
    lower_limit: Mapped[int | None] = mapped_column(nullable=True)
