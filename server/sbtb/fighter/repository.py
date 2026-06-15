from datetime import datetime
from typing import Sequence

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import joinedload

from sbtb.core.repository.base import BaseRepository
from sbtb.fighter.schemas import BoutInput, RankInput
from sbtb.models import Bout, FeaturedFighter, FightCard, Fighter, FightOrganization, Rank, WeightClass
from sbtb.models.featured_fighter import FeaturedCollection


class FighterRepo(BaseRepository[Fighter]):
    model = Fighter

    async def get_by_name(self, name: str) -> Fighter | None:
        return await self.get_one_or_none(self.get_base_statement().where(Fighter.name == name))

    async def get_or_create(self, name: str) -> Fighter:
        fighter = await self.get_by_name(name)
        if not fighter:
            fighter = Fighter(name=name)
            await self.create(fighter, flush=True)
        return fighter

    async def get_without_avatar(self) -> Sequence[Fighter]:
        return await self.get_all(self.get_base_statement().where(Fighter.avatar_url.is_(None)))

    async def upsert(self, name: str, **kwargs) -> Fighter:
        fighter = await self.get_by_name(name)
        if fighter:
            await self.update(fighter, update_dict=kwargs, flush=True)
        else:
            fighter = Fighter(name=name, **kwargs)
            await self.create(fighter, flush=True)
        return fighter


class FeaturedFighterRepo(BaseRepository[FeaturedFighter]):
    model = FeaturedFighter

    async def get_by_collection(self, collection: FeaturedCollection) -> Sequence[FeaturedFighter]:
        statement = (
            self.get_base_statement()
            .options(joinedload(FeaturedFighter.fighter))
            .where(FeaturedFighter.collection == collection)
            .order_by(FeaturedFighter.position.asc().nulls_last(), FeaturedFighter.created_at.asc())
        )
        return await self.get_all(statement)


class RankRepo(BaseRepository[Rank]):
    model = Rank

    async def bulk_upsert(self, ranks: list[RankInput]) -> Sequence[Rank]:
        if not ranks:
            return []

        # Full refresh: scraper fetches all rankings each run, so delete and re-insert
        await self.session.execute(delete(Rank))

        rank_dicts = [r.model_dump(exclude={"id"}) for r in ranks]
        stmt = pg_insert(Rank).values(rank_dicts).returning(Rank)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class FightOrganizationRepo(BaseRepository[FightOrganization]):
    model = FightOrganization


class WeightClassRepo(BaseRepository[WeightClass]):
    model = WeightClass


class FightCardRepo(BaseRepository[FightCard]):
    model = FightCard

    async def get_or_create(
        self,
        *,
        event_name: str,
        event_date: datetime,
        location: str | None = None,
        network: str | None = None,
    ) -> FightCard:
        card = await self.get_one_or_none(
            self.get_base_statement().where(
                FightCard.event_name == event_name,
                FightCard.event_date == event_date,
            )
        )
        if not card:
            card = FightCard(
                event_name=event_name,
                event_date=event_date,
                location=location,
                network=network,
            )
            await self.create(card, flush=True)
        return card

    async def upsert_bouts(self, fight_card: FightCard, bouts: list[BoutInput]) -> FightCard:
        await self.session.execute(delete(Bout).where(Bout.fight_card_id == fight_card.id))
        for bout_input in bouts:
            await self.create(
                Bout(
                    fight_card_id=fight_card.id,
                    red_corner_id=bout_input.red_corner_id,
                    blue_corner_id=bout_input.blue_corner_id,
                    bout_order=bout_input.bout_order,
                    is_title_fight=bout_input.is_title_fight,
                )
            )

        await self.session.flush()

        # Re-query to get the card with freshly loaded bouts
        return await self.get_one_or_none(self.get_base_statement().where(FightCard.id == fight_card.id))
