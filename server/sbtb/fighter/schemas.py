import datetime

from pydantic import UUID4, BaseModel

from sbtb.core.schemas import BaseSchema, IDSchema
from sbtb.models.rank import RankType

# --- Internal DTOs (not for API responses) ---


class RawBoxerSchema(BaseModel):
    name: str
    rank_type: RankType
    position: int | None = None  # 1–15 for contenders, None for champion types


class ParsedFightCard(BaseModel):
    fight_date: datetime.datetime
    title_fighters: list[str]
    undercard_fighters: list[str]
    location: str
    network: str | None = None


class RankInput(BaseSchema):
    id: UUID4 | None = None
    rank_type: RankType
    position: int | None = None
    fighter_id: UUID4
    weight_class_id: UUID4
    organization_id: UUID4


class BoutInput(BaseSchema):
    red_corner_id: UUID4
    blue_corner_id: UUID4
    bout_order: int | None = None
    is_title_fight: bool = False


# --- API Response Schemas ---


class AvatarGenerationResult(BaseSchema):
    updated: list[str]
    skipped: list[str]


class FighterRead(IDSchema):
    name: str
    nickname: str | None = None
    age: int | None = None
    wins: int | None = None
    losses: int | None = None
    draws: int | None = None


class FeaturedFighterRead(IDSchema):
    name: str
    avatar_url: str | None = None


class WeightClassRead(IDSchema):
    name: str
    pounds: int | None = None


class FightOrganizationRead(IDSchema):
    name: str | None = None


class RankRead(BaseSchema):
    rank_type: RankType
    position: int | None
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
    event_date: datetime.datetime
    bouts: list[BoutRead] = []
