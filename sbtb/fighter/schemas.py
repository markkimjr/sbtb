from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


class RawBoxerSchema(BaseModel):
    name: str
    rank: float
    is_champ: Optional[bool] = False


class FighterSchema(BaseModel):
    name: str
    nickname: Optional[str] = None
    age: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None

    class Config:
        from_attributes = True


class RankSchema(BaseModel):
    rank: float
    fighter_id: int
    weight_class_id: int
    organization_id: int

    class Config:
        from_attributes = True


class WeightClassSchema(BaseModel):
    name: str
    pounds: Optional[int] = None
    kilos: Optional[int] = None
    upper_limit: Optional[int] = None
    lower_limit: Optional[int] = None

    class Config:
        from_attributes = True


class FightingOrganizationSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True


class FightCardSchema(BaseModel):
    event_name: str
    location: str
    event_date: datetime

    class Config:
        from_attributes = True
