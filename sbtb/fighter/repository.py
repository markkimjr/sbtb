from typing import Optional, List
from sqlalchemy import select, or_

from sbtb.database.session import DbSession
from sbtb.fighter.schemas import FighterSchema
from sbtb.fighter.models import Fighter


class FighterRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[Fighter]:
        return await self.db.get(Fighter, user_id)

    async def get_by_name_or_nickname(
        self,
        name: str,
        nickname: str,
    ) -> Optional[Fighter]:
        query = await self.db.execute(
            select(Fighter).where(or_(Fighter.name == name, Fighter.nickname == nickname))
        )

        return query.scalars().first()

    async def get_fighters(self) -> List[Fighter]:
        query = await self.db.execute(select(Fighter))
        return query.scalars().all()

    async def save(self, raw_fighter: FighterSchema) -> Fighter:
        fighter = Fighter(**raw_fighter.model_dump())
        self.db.add(fighter)
        await self.db.commit()
        await self.db.refresh(fighter)
        return fighter
