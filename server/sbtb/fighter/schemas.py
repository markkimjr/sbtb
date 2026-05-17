from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


class RawBoxerSchema(BaseModel):
    name: str
    rank: float
    is_champ: Optional[bool] = False


class FighterRead(BaseModel):
    name: str
    nickname: Optional[str] = None
    age: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None

    class Config:
        from_attributes = True


class RankRead(BaseModel):
    rank: float
    fighter_name: str
    weight_class_name: str
    organization_name: str


class WeightClassRead(BaseModel):
    name: str
    pounds: Optional[int] = None
    kilos: Optional[int] = None
    upper_limit: Optional[int] = None
    lower_limit: Optional[int] = None

    class Config:
        from_attributes = True


class FightOrganizationRead(BaseModel):
    name: str

    class Config:
        from_attributes = True


class FightCardRead(BaseModel):
    event_name: str
    location: str
    event_date: datetime
    fighters: List[FighterRead] = []

    class Config:
        from_attributes = True
