from pydantic import BaseModel
from typing import List, Optional

class FighterSchema(BaseModel):
    name: str
    nickname: Optional[str] = None
    age: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None
    fighting_organizations: List[str]
    weight_classes: List[str]

    class Config:
        from_attributes = True


class WeightClassSchema(BaseModel):
    name: str
    upper_limit: Optional[int] = None
    lower_limit: Optional[int] = None

    class Config:
        from_attributes = True


class FightingOrganizationSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True
