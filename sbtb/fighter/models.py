from enum import Enum
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM
from sbtb.database.session import Base


class FighterWeightClassAssociation(Base):
    __tablename__ = "fighter_weight_class_association"

    fighter_id: Mapped[int] = mapped_column(
        ForeignKey("fighters.id"),
        primary_key=True,
    )
    weight_class_id: Mapped[int] = mapped_column(
        ForeignKey("weight_classes.id"),
        primary_key=True,
    )


class FighterFightOrganizationAssociation(Base):
    __tablename__ = "fighter_fight_organization_association"

    fighter_id: Mapped[int] = mapped_column(
        ForeignKey("fighters.id"),
        primary_key=True,
    )
    fight_organization_id: Mapped[int] = mapped_column(
        ForeignKey("fight_organizations.id"),
        primary_key=True,
    )


class FightOrganization(Base):
    __tablename__ = "fight_organizations"

    class FightOrganizationEnum(Enum):
        UFC = "UFC"
        WBO = "WBO"
        WBC = "WBC"
        IBF = "IBF"
        WBA = "WBA"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(ENUM(FightOrganizationEnum), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    fighters: Mapped[list["Fighter"]] = relationship(
        "Fighter",
        secondary="fighter_fight_organization_association",
        backref="fight_organizations"
    )


class WeightClass(Base):
    __tablename__ = "weight_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    upper_limit = Column(Integer, nullable=True)
    lower_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    fighters: Mapped[list["Fighter"]] = relationship(
        "Fighter",
        secondary="fighter_weight_class_association",
        backref="weight_classes"
    )


class Fighter(Base):
    __tablename__ = "fighters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    nickname = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=True, default=0)
    losses = Column(Integer, nullable=True, default=0)
    draws = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    weight_classes: Mapped[list["WeightClass"]] = relationship(
        "WeightClass",
        secondary="fighter_weight_class_association",
        backref="fighters"
    )

    fighting_organizations: Mapped[list["FightOrganization"]] = relationship(
        "FightOrganization",
        secondary="fighter_fight_organization_association",
        backref="fighters"
    )

