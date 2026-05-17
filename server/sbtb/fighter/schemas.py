from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel

from sbtb.core.schemas import BaseSchema, IDSchema

# --- Internal DTOs (not for API responses) ---


class RawBoxerSchema(BaseModel):
    name: str
    rank: float
    is_champ: bool = False


class RankInput(BaseSchema):
    id: UUID4 | None = None
    rank: float
    fighter_id: UUID4
    weight_class_id: UUID4
    organization_id: UUID4


class BoutInput(BaseSchema):
    red_corner_id: UUID4
    blue_corner_id: UUID4
    bout_order: int | None = None
    is_title_fight: bool = False


# --- API Response Schemas ---


class FighterRead(IDSchema):
    name: str
    nickname: str | None = None
    age: int | None = None
    wins: int | None = None
    losses: int | None = None
    draws: int | None = None


class WeightClassRead(IDSchema):
    name: str
    pounds: int | None = None
    kilos: int | None = None
    upper_limit: int | None = None
    lower_limit: int | None = None


class FightOrganizationRead(IDSchema):
    name: str | None = None


class RankRead(BaseSchema):
    rank: float
    fighter_name: str
    weight_class_name: str
    organization_name: str


class BoutRead(IDSchema):
    bout_order: int | None = None
    is_title_fight: bool
    red_corner: FighterRead
    blue_corner: FighterRead


class FightCardRead(IDSchema):
    event_name: str | None = None
    location: str | None = None
    event_date: datetime
    bouts: List[BoutRead] = []
