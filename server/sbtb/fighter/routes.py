from typing import List

from fastapi import Depends
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response

from sbtb.fighter.dependencies import get_boxer_scraper_service, get_boxing_fight_card_service
from sbtb.fighter.schemas import FightCardRead, RankRead
from sbtb.fighter.service import BoxerScraperService, BoxingFightCardService
from sbtb.fighter.domain import FightCardDomain

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
async def scrape_and_save_boxing_ranks(
        service: BoxerScraperService = Depends(get_boxer_scraper_service)
) -> List[RankRead]:
    updated_ranks: List[RankRead] = await service.scrape_and_update_boxing_ranks()
    return updated_ranks


@router.get("/update-boxing-fight-cards",
            response_description="Update boxing fight cards",
            response_model=List[FightCardRead],
            tags=["fighters"])
async def scrape_and_save_boxing_fight_cards(
        service: BoxingFightCardService = Depends(get_boxing_fight_card_service)
) -> List[FightCardRead]:
    updated_fight_cards: List[FightCardDomain] = await service.scrape_and_update_boxing_fight_cards()
    fight_card_reads = [FightCardRead.model_validate(fc) for fc in updated_fight_cards]
    return fight_card_reads
