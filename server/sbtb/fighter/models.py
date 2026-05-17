from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import ForeignKey, Double, String, Table, Column, Uuid, TIMESTAMP
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from sbtb.core.database.base import RecordModel, BaseModel


class FightOrganization(RecordModel):
    __tablename__ = "fight_organizations"

    class FightOrganizationEnum(Enum):
        UFC = "UFC"
        WBO = "WBO"
        WBC = "WBC"
        IBF = "IBF"
        WBA = "WBA"

    name: Mapped[str | None] = mapped_column(ENUM(FightOrganizationEnum), nullable=True)


class WeightClass(RecordModel):
    __tablename__ = "weight_classes"

    name: Mapped[str] = mapped_column(String, nullable=False)
    pounds: Mapped[int | None] = mapped_column(nullable=True)
    kilos: Mapped[int | None] = mapped_column(nullable=True)
    upper_limit: Mapped[int | None] = mapped_column(nullable=True)
    lower_limit: Mapped[int | None] = mapped_column(nullable=True)


class Rank(RecordModel):
    __tablename__ = "ranks"

    rank: Mapped[float] = mapped_column(Double, nullable=False)
    fighter_id: Mapped[UUID] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    weight_class_id: Mapped[UUID] = mapped_column(ForeignKey("weight_classes.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("fight_organizations.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("rank", "weight_class_id", "organization_id"),
    )


fight_card_fighters = Table(
    "fight_card_fighters",
    BaseModel.metadata,
    Column("fight_card_id", Uuid, ForeignKey("fight_cards.id"), primary_key=True),
    Column("fighter_id", Uuid, ForeignKey("fighters.id"), primary_key=True),
)


class Fighter(RecordModel):
    __tablename__ = "fighters"

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    nickname: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[int | None] = mapped_column(nullable=True)
    wins: Mapped[int | None] = mapped_column(nullable=True, default=0)
    losses: Mapped[int | None] = mapped_column(nullable=True, default=0)
    draws: Mapped[int | None] = mapped_column(nullable=True, default=0)

    fight_cards: Mapped[list["FightCard"]] = relationship(
        "FightCard", secondary=fight_card_fighters, back_populates="fighters", lazy="selectin"
    )


class FightCard(RecordModel):
    __tablename__ = "fight_cards"

    event_name: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    network: Mapped[str | None] = mapped_column(String, nullable=True)
    event_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    fighters: Mapped[list[Fighter]] = relationship(
        "Fighter", secondary=fight_card_fighters, back_populates="fight_cards", lazy="selectin"
    )
