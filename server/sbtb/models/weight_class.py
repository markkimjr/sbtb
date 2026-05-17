from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from sbtb.core.database.base import RecordModel


class WeightClass(RecordModel):
    __tablename__ = "weight_classes"

    name: Mapped[str] = mapped_column(String, nullable=False)
    pounds: Mapped[int | None] = mapped_column(nullable=True)

    __table_args__ = (UniqueConstraint("name", name="uq_weight_classes_name"),)
