from typing import Optional, List

from sqlalchemy import select, or_

from sbtb.database.session import DbSession
from sbtb.fighter.schemas import FighterSchema, RankSchema, FightCardSchema
from sbtb.fighter.models import Fighter, Rank, FightOrganization, WeightClass, FightCard


class FighterRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    async def get_by_id(self, fighter_id: int) -> Optional[Fighter]:
        return await self.db.get(Fighter, fighter_id)

    async def get_by_name(
            self,
            name: str
    ) -> Optional[Fighter]:
        query = await self.db.execute(
            select(Fighter).where(or_(Fighter.name == name))
        )
        return query.scalars().first()

    async def get_all(self) -> List[Fighter]:
        query = await self.db.execute(select(Fighter))
        return query.scalars().all()

    async def get_or_create(self, raw_fighter: FighterSchema) -> Fighter:
        query = await self.db.execute(select(Fighter).where(Fighter.name == raw_fighter.name))
        fighter = query.scalars().first()
        if not fighter:
            # add raw_fighter
            fighter = Fighter(**raw_fighter.model_dump())
            self.db.add(fighter)
            await self.db.commit()
            await self.db.refresh(fighter)
        return fighter

    async def upsert(self, raw_fighter: FighterSchema) -> Fighter:
        query = await self.db.execute(select(Fighter).where(Fighter.name == raw_fighter.name))
        existing_fighter = query.scalars().first()

        if existing_fighter:
            for key, value in raw_fighter.model_dump().items():
                setattr(existing_fighter, key, value)
            fighter = existing_fighter
        else:
            fighter = Fighter(**raw_fighter.model_dump())
            self.db.add(fighter)

        await self.db.commit()
        await self.db.refresh(fighter)
        return fighter

    async def bulk_upsert(self, raw_fighters: List[FighterSchema]) -> List[Fighter]:
        fighter_objects = []
        for raw_fighter in raw_fighters:
            existing_fighter = await self.get_by_name(raw_fighter.name)
            if existing_fighter:
                for key, value in raw_fighter.model_dump().items():
                    setattr(existing_fighter, key, value)
                fighter_objects.append(existing_fighter)
            else:
                new_fighter = Fighter(**raw_fighter.model_dump())
                fighter_objects.append(new_fighter)

        self.db.add_all(fighter_objects)
        await self.db.commit()
        return fighter_objects

    async def save(self, fighter: Fighter) -> Fighter:
        self.db.add(fighter)
        await self.db.commit()
        await self.db.refresh(fighter)
        return fighter

class RankRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    async def get_by_id(self, rank_id: int) -> Optional[RankSchema]:
        return await self.db.get(RankSchema, rank_id)

    async def bulk_upsert(self, ranks: List[RankSchema]) -> List[Rank]:
        rank_objects = []
        for rank in ranks:
            existing_rank = await self.db.execute(
                select(Rank).where(
                    Rank.fighter_id == rank.fighter_id,
                    Rank.weight_class_id == rank.weight_class_id,
                    Rank.organization_id == rank.organization_id
                )
            )
            existing_rank = existing_rank.scalars().first()
            if existing_rank:
                for key, value in rank.model_dump().items():
                    setattr(existing_rank, key, value)
                rank_objects.append(existing_rank)
            else:
                new_rank = Rank(**rank.model_dump())
                self.db.add(new_rank)
                rank_objects.append(new_rank)

        await self.db.commit()
        return rank_objects


class FightingOrganizationRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    async def get_by_id(self, org_id: int) -> Optional[FightOrganization]:
        return await self.db.get(FightOrganization, org_id)

    async def get_by_name(
            self,
            name: str
    ) -> Optional[FightOrganization]:
        query = await self.db.execute(
            select(FightOrganization).where(or_(FightOrganization.name == name))
        )
        return query.scalars().first()

    async def get_all(self) -> List[FightOrganization]:
        query = await self.db.execute(select(FightOrganization))
        return query.scalars().all()


class WeightClassRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    async def get_by_id(self, weight_class_id: int) -> Optional[WeightClass]:
        return await self.db.get(WeightClass, weight_class_id)

    async def get_by_name(
            self,
            name: str
    ) -> Optional[WeightClass]:
        query = await self.db.execute(
            select(WeightClass).where(or_(WeightClass.name == name))
        )
        return query.scalars().first()

    async def get_all(self) -> List[WeightClass]:
        query = await self.db.execute(select(WeightClass))
        return query.scalars().all()


class FightCardRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    async def get_by_id(self, fight_card_id: int) -> Optional[FightCard]:
        return await self.db.get(FightCard, fight_card_id)

    async def get_or_create(self, raw_fight_card: FightCardSchema, eager=False) -> FightCard:
        query = await self.db.execute(
            select(FightCard).where(FightCard.event_name == raw_fight_card.event_name)
        )
        fight_card = query.scalars().first()
        if not fight_card:
            fight_card = FightCard(**raw_fight_card.model_dump())
            self.db.add(fight_card)
            await self.db.commit()
            await self.db.refresh(fight_card)
        return fight_card

    async def upsert(self, raw_fight_card: FightCardSchema) -> FightCard:
        query = await self.db.execute(select(FightCard).where(FightCard.event_name == raw_fight_card.event_name))
        existing_fight_card = query.scalars().first()

        if existing_fight_card:
            for key, value in raw_fight_card.model_dump().items():
                setattr(existing_fight_card, key, value)
            fight_card = existing_fight_card
        else:
            fight_card = FightCard(**raw_fight_card.model_dump())
            self.db.add(fight_card)

        await self.db.commit()
        await self.db.refresh(fight_card)
        return fight_card

    async def save(self, fight_card: FightCard) -> FightCard:
        self.db.add(fight_card)
        await self.db.commit()
        await self.db.refresh(fight_card)
        return fight_card
