import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class FighterDomain(BaseModel):
    id: Optional[UUID] = None
    name: str
    nickname: Optional[str] = None
    age: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None

    class Config:
        from_attributes = True


class RankDomain(BaseModel):
    id: Optional[UUID] = None
    rank: float
    fighter_id: UUID
    weight_class_id: UUID
    organization_id: UUID

    class Config:
        from_attributes = True


class FightCardDomain(BaseModel):
    id: Optional[UUID] = None
    event_name: str
    location: str
    event_date: datetime.datetime
    fighters: List[FighterDomain] = []

    class Config:
        from_attributes = True

    def set_fighters(self, fighters: List[FighterDomain]):
        self.fighters = fighters


class WeightClassDomain(BaseModel):
    id: Optional[UUID] = None
    name: str
    pounds: Optional[int] = None
    kilos: Optional[int] = None
    upper_limit: Optional[int] = None
    lower_limit: Optional[int] = None

    class Config:
        from_attributes = True


class FightOrganizationDomain(BaseModel):
    id: Optional[UUID] = None
    name: str

    class Config:
        from_attributes = True
