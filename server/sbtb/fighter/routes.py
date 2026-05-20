from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response

from sbtb.auth.permissions import SuperuserDep
from sbtb.core.database.session import DbSession
from sbtb.fighter.image_generator import fighter_image_generator
from sbtb.fighter.schemas import AvatarGenerationResult, FightCardRead, RankRead
from sbtb.fighter.service import boxer_scraper_service, boxing_fight_card_service

router = APIRouter(prefix="/fighter")


@router.get("/", response_description="Fighter Root", include_in_schema=False)
async def fighter_root() -> Response:
    return JSONResponse(
        content={"message": "Welcome to Fighter API"},
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/update-boxing-ranks", response_description="Update boxing ranks", response_model=list[RankRead], tags=["fighters"]
)
async def scrape_and_save_boxing_ranks(session: DbSession) -> list[RankRead]:
    return await boxer_scraper_service.scrape_and_update_boxing_ranks(session=session)


@router.get(
    "/update-boxing-fight-cards",
    response_description="Update boxing fight cards",
    response_model=list[FightCardRead],
    tags=["fighters"],
)
async def scrape_and_save_boxing_fight_cards(session: DbSession) -> list[FightCardRead]:
    return await boxing_fight_card_service.scrape_and_update_boxing_fight_cards(session=session)


@router.post(
    "/generate-avatars",
    response_description="Generate Ghibli avatars for fighters missing one",
    response_model=AvatarGenerationResult,
    tags=["fighters"],
)
async def generate_fighter_avatars(session: DbSession, _: SuperuserDep) -> AvatarGenerationResult:
    return await fighter_image_generator.generate_fighter_avatars(session=session)
