from typing import List

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response

from sbtb.core.database.session import DbSession
from sbtb.fighter.schemas import FightCardRead, RankRead
from sbtb.fighter.service import boxer_scraper_service, boxing_fight_card_service

router = APIRouter(prefix="/fighter")


@router.get("/",
            response_description="Fighter Root",
            include_in_schema=False)
async def fighter_root() -> Response:
    return JSONResponse(
        content={"message": "Welcome to Fighter API"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/update-boxing-ranks",
            response_description="Update boxing ranks",
            response_model=List[RankRead],
            tags=["fighters"])
async def scrape_and_save_boxing_ranks(session: DbSession) -> List[RankRead]:
    return await boxer_scraper_service.scrape_and_update_boxing_ranks(session=session)


@router.get("/update-boxing-fight-cards",
            response_description="Update boxing fight cards",
            response_model=List[FightCardRead],
            tags=["fighters"])
async def scrape_and_save_boxing_fight_cards(session: DbSession) -> List[FightCardRead]:
    return await boxing_fight_card_service.scrape_and_update_boxing_fight_cards(session=session)
