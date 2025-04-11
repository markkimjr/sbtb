import datetime
from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import func

from sbtb.database.session import DbSession
from sbtb.fighter.models import Fighter, Rank, FightOrganization, WeightClass, FightCard
from sbtb.fighter.domain import FighterDomain, RankDomain, FightCardDomain, FightOrganizationDomain, WeightClassDomain


class FighterRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    @staticmethod
    def to_domain(fighter_orm: Fighter) -> FighterDomain:
        return FighterDomain.model_validate(fighter_orm)

    @staticmethod
    def from_domain(fighter_domain: FighterDomain) -> Fighter:
        return Fighter(**fighter_domain.model_dump(exclude_unset=True))

    async def get_by_id(self, fighter_id: int) -> Optional[FighterDomain]:
        fighter = await self.db.get(Fighter, fighter_id)
        return self.to_domain(fighter) if fighter else None

    async def get_by_name(self, name: str) -> Optional[FighterDomain]:
        query = await self.db.execute(
            select(Fighter).where(Fighter.name == name)
        )
        fighter = query.scalars().first()
        return self.to_domain(fighter) if fighter else None

    async def get_all(self) -> List[FighterDomain]:
        query = await self.db.execute(select(Fighter))
        fighters = query.scalars().all()
        return [self.to_domain(f) for f in fighters]

    async def get_or_create(self, raw_fighter: FighterDomain) -> FighterDomain:
        query = await self.db.execute(select(Fighter).where(Fighter.name == raw_fighter.name))
        fighter = query.scalars().first()
        if not fighter:
            fighter = self.from_domain(raw_fighter)
            self.db.add(fighter)
            await self.db.commit()
            await self.db.refresh(fighter)
        return self.to_domain(fighter)

    async def upsert(self, raw_fighter: FighterDomain) -> FighterDomain:
        query = await self.db.execute(select(Fighter).where(Fighter.name == raw_fighter.name))
        existing_fighter = query.scalars().first()

        if existing_fighter:
            for key, value in raw_fighter.model_dump(exclude_unset=True).items():
                setattr(existing_fighter, key, value)
            fighter = existing_fighter
        else:
            fighter = self.from_domain(raw_fighter)
            self.db.add(fighter)

        await self.db.commit()
        await self.db.refresh(fighter)
        return self.to_domain(fighter)

    async def bulk_upsert(self, fighters: List[FighterDomain]) -> List[FighterDomain]:
        fighter_objects = []
        for raw_fighter in fighters:
            existing_fighter = await self.db.execute(select(Fighter).where(Fighter.name == raw_fighter.name))
            existing = existing_fighter.scalars().first()
            if existing:
                for key, value in raw_fighter.model_dump(exclude_unset=True).items():
                    setattr(existing, key, value)
                fighter_objects.append(existing)
            else:
                new_fighter = self.from_domain(raw_fighter)
                fighter_objects.append(new_fighter)

        self.db.add_all(fighter_objects)
        await self.db.commit()
        return [self.to_domain(f) for f in fighter_objects]

    async def save(self, fighter: FighterDomain) -> FighterDomain:
        orm_fighter = self.from_domain(fighter)
        self.db.add(orm_fighter)
        await self.db.commit()
        await self.db.refresh(orm_fighter)
        return self.to_domain(orm_fighter)


class RankRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    @staticmethod
    def to_domain(rank_orm: Rank) -> RankDomain:
        return RankDomain.model_validate(rank_orm)

    @staticmethod
    def from_domain(rank_domain: RankDomain) -> Rank:
        return Rank(**rank_domain.model_dump(exclude_unset=True))

    async def get_by_id(self, rank_id: int) -> Optional[RankDomain]:
        rank_orm = await self.db.get(Rank, rank_id)
        if not rank_orm:
            return None
        return self.to_domain(rank_orm)

    async def bulk_upsert(self, ranks: List[RankDomain]) -> List[RankDomain]:
        if not ranks:
            return []

        rank_dicts = [r.model_dump(exclude_unset=True) for r in ranks]

        stmt = pg_insert(Rank).values(rank_dicts)

        update_columns = {
            "fighter_id": stmt.excluded.fighter_id,
            "updated_at": func.now(),
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=["rank", "weight_class_id", "organization_id"],
            set_=update_columns
        ).returning(Rank)

        result = await self.db.execute(stmt)
        await self.db.commit()

        upserted_ranks = result.scalars().all()
        return [self.to_domain(rank) for rank in upserted_ranks]


class FightOrganizationRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    @staticmethod
    def to_domain(fight_org_orm: FightOrganization) -> FightOrganizationDomain:
        return FightOrganizationDomain.model_validate(fight_org_orm)

    @staticmethod
    def from_domain(fight_org_domain: FightOrganizationDomain) -> FightOrganization:
        return FightOrganization(**fight_org_domain.model_dump(exclude_unset=True))

    async def get_all(self) -> List[FightOrganizationDomain]:
        query = await self.db.execute(select(FightOrganization))
        fight_orgs = query.scalars().all()
        return [self.to_domain(f) for f in fight_orgs]


class WeightClassRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    @staticmethod
    def to_domain(weight_class_orm: WeightClass) -> WeightClassDomain:
        return WeightClassDomain.model_validate(weight_class_orm)

    @staticmethod
    def from_domain(weight_class_domain: WeightClassDomain) -> WeightClass:
        return WeightClass(**weight_class_domain.model_dump(exclude_unset=True))

    async def get_all(self) -> List[WeightClassDomain]:
        query = await self.db.execute(select(WeightClass))
        weight_classes = query.scalars().all()
        return [self.to_domain(f) for f in weight_classes]


class FightCardRepo:
    def __init__(self, db: DbSession, *args, **kwargs):
        self.db = db

    def to_domain(self, orm_card: FightCard) -> FightCardDomain:
        return FightCardDomain(
            id=orm_card.id,
            event_name=orm_card.event_name,
            location=orm_card.location,
            event_date=orm_card.event_date,
            fighters=[
                FighterDomain(id=f.id, name=f.name)
                for f in orm_card.fighters
            ] if orm_card.fighters else []
        )

    async def _create_from_domain(self, fight_card_domain: FightCardDomain) -> FightCard:
        orm_card = FightCard(**fight_card_domain.model_dump(exclude={"id", "fighters"}))

        if fight_card_domain.fighters:
            fighter_ids = [f.id for f in fight_card_domain.fighters if f.id]
            if fighter_ids:
                result = await self.db.execute(
                    select(Fighter).where(Fighter.id.in_(fighter_ids))
                )
                fighters = result.scalars().all()
                orm_card.fighters = fighters

        self.db.add(orm_card)
        await self.db.commit()
        await self.db.refresh(orm_card)
        return orm_card

    async def _update_fighters(self, orm_card: FightCard, domain_fighters: list[FighterDomain]):
        fighter_ids = [f.id for f in domain_fighters if f.id]
        result = await self.db.execute(select(Fighter).where(Fighter.id.in_(fighter_ids)))
        orm_card.fighters = result.scalars().all()

    async def get_by_id(self, fight_card_id: int) -> Optional[FightCardDomain]:
        orm_fight_card = await self.db.get(FightCard, fight_card_id)
        if orm_fight_card:
            await self.db.refresh(orm_fight_card)
            return self.to_domain(orm_fight_card)
        return None

    async def get_or_create(self, fight_card_domain: FightCardDomain) -> FightCardDomain:
        query = await self.db.execute(
            select(FightCard).where(FightCard.event_name == fight_card_domain.event_name)
        )
        orm_fight_card = query.scalars().first()

        if not orm_fight_card:
            orm_fight_card = await self._create_from_domain(fight_card_domain)

        return self.to_domain(orm_fight_card)

    async def upsert(self, fight_card_domain: FightCardDomain) -> FightCardDomain:
        query = await self.db.execute(
            select(FightCard).where(FightCard.event_name == fight_card_domain.event_name)
        )
        existing = query.scalars().first()

        if existing:
            for key, value in fight_card_domain.model_dump(exclude={"id", "fighters"}).items():
                setattr(existing, key, value)
            await self._update_fighters(existing, fight_card_domain.fighters)
            await self.db.commit()
            await self.db.refresh(existing)
            return self.to_domain(existing)

        new_orm = await self._create_from_domain(fight_card_domain)
        return self.to_domain(new_orm)

    async def save(self, fight_card_domain: FightCardDomain) -> FightCardDomain:
        orm_card = await self._create_from_domain(fight_card_domain)
        return self.to_domain(orm_card)
