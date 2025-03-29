from enum import Enum
from sqlalchemy import ForeignKey, Column, Integer, Double, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sbtb.database.session import Base


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


class WeightClass(Base):
    __tablename__ = "weight_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    pounds = Column(Integer, nullable=True)
    kilos = Column(Integer, nullable=True)
    upper_limit = Column(Integer, nullable=True)
    lower_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)


class Rank(Base):
    __tablename__ = "ranks"

    id = Column(Integer, primary_key=True, index=True)
    rank = Column(Double, nullable=False)
    fighter_id = Column(Integer, ForeignKey("fighters.id"), nullable=False)
    weight_class_id = Column(Integer, ForeignKey("weight_classes.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("fight_organizations.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("rank", "weight_class_id", "organization_id"),
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
