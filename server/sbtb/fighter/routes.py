from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response

from sbtb.auth.permissions import SuperuserDep
from sbtb.core.database.session import DbSession
from sbtb.fighter.avatar_generators import gemini_fighter_image_generator
from sbtb.fighter.schemas import AvatarGenerationResult, FeaturedFighterRead, FightCardRead, RankRead
from sbtb.fighter.service import boxer_scraper_service, boxing_fight_card_service, featured_fighter_service
from sbtb.models.featured_fighter import FeaturedCollection

router = APIRouter(prefix="/fighter")


@router.get("/", response_description="Fighter Root", include_in_schema=False)
async def fighter_root() -> Response:
    return JSONResponse(
        content={"message": "Welcome to Fighter API"},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/update-boxing-ranks",
    response_description="Update boxing ranks",
    response_model=list[RankRead],
    tags=["fighters"],
)
async def scrape_and_save_boxing_ranks(
    session: DbSession,
    _superuser: SuperuserDep,
) -> list[RankRead]:
    return await boxer_scraper_service.scrape_and_update_boxing_ranks(session=session)


@router.get(
    "/update-boxing-fight-cards",
    response_description="Update boxing fight cards",
    response_model=list[FightCardRead],
    tags=["fighters"],
)
async def scrape_and_save_boxing_fight_cards(
    session: DbSession,
    _superuser: SuperuserDep,
) -> list[FightCardRead]:
    return await boxing_fight_card_service.scrape_and_update_boxing_fight_cards(session=session)


@router.post(
    "/generate-avatars",
    response_description="Generate Ghibli avatars for fighters missing one",
    response_model=AvatarGenerationResult,
    tags=["fighters"],
)
async def generate_fighter_avatars(
    session: DbSession,
    _superuser: SuperuserDep,
) -> AvatarGenerationResult:
    return await gemini_fighter_image_generator.generate_fighter_avatars(session=session)


@router.get(
    "/featured",
    response_description="List featured fighters for a curated collection",
    response_model=list[FeaturedFighterRead],
    tags=["fighters"],
)
async def get_featured_fighters(
    session: DbSession,
    collection: FeaturedCollection = FeaturedCollection.popular_fighters,
) -> list[FeaturedFighterRead]:
    return await featured_fighter_service.get_by_collection(session=session, collection=collection)
