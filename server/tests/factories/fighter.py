from uuid import uuid4

from sbtb.models import FeaturedFighter, Fighter
from sbtb.models.featured_fighter import FeaturedCollection
from tests.fixtures.database import SaveFixture


async def create_test_fighter(
    save_fixture: SaveFixture,
    name: str | None = None,
    avatar_url: str | None = None,
    wins: int = 0,
    losses: int = 0,
    draws: int = 0,
) -> Fighter:
    fighter = Fighter(
        id=uuid4(),
        name=name or f"Test Fighter {uuid4().hex[:8]}",
        avatar_url=avatar_url,
        wins=wins,
        losses=losses,
        draws=draws,
    )
    await save_fixture(fighter)
    return fighter


async def create_test_featured_fighter(
    save_fixture: SaveFixture,
    fighter: Fighter,
    collection: FeaturedCollection = FeaturedCollection.popular_fighters,
    position: int | None = None,
) -> FeaturedFighter:
    featured = FeaturedFighter(
        id=uuid4(),
        fighter_id=fighter.id,
        collection=collection,
        position=position,
    )
    await save_fixture(featured)
    return featured
