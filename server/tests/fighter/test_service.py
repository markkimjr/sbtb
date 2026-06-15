import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from sbtb.fighter.service import FeaturedFighterService
from sbtb.models.featured_fighter import FeaturedCollection
from tests.factories import create_test_featured_fighter, create_test_fighter
from tests.fixtures.database import SaveFixture


@pytest.mark.asyncio
class TestFeaturedFighterServiceGetByCollection:
    async def test_returns_empty_when_no_featured_fighters(self, session: AsyncSession) -> None:
        service = FeaturedFighterService()

        result = await service.get_by_collection(session=session, collection=FeaturedCollection.popular_fighters)

        assert result == []

    async def test_returns_fighters_for_collection(self, session: AsyncSession, save_fixture: SaveFixture) -> None:
        fighter = await create_test_fighter(save_fixture, name="Canelo", avatar_url="https://example.com/c.webp")
        await create_test_featured_fighter(save_fixture, fighter=fighter, position=1)
        service = FeaturedFighterService()

        result = await service.get_by_collection(session=session, collection=FeaturedCollection.popular_fighters)

        assert len(result) == 1
        assert result[0].name == "Canelo"
        assert result[0].avatar_url == "https://example.com/c.webp"

    async def test_orders_by_position_then_created_at(self, session: AsyncSession, save_fixture: SaveFixture) -> None:
        # Fighter A has no position (NULLS LAST); B is position 2; C is position 1.
        fighter_a = await create_test_fighter(save_fixture, name="A")
        fighter_b = await create_test_fighter(save_fixture, name="B")
        fighter_c = await create_test_fighter(save_fixture, name="C")
        await create_test_featured_fighter(save_fixture, fighter=fighter_a, position=None)
        await create_test_featured_fighter(save_fixture, fighter=fighter_b, position=2)
        await create_test_featured_fighter(save_fixture, fighter=fighter_c, position=1)
        service = FeaturedFighterService()

        result = await service.get_by_collection(session=session, collection=FeaturedCollection.popular_fighters)

        assert [f.name for f in result] == ["C", "B", "A"]
