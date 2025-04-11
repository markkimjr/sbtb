from typing import List

from fastapi import Depends
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder

from sbtb.fighter.dependencies import get_boxer_repo, get_boxing_scraper, get_boxer_org_repo, get_rank_repo, \
    get_weight_class_repo, get_boxing_fight_card_scraper, get_fight_card_repo
from sbtb.fighter.schemas import FightCardRead, RankRead
from sbtb.fighter.service import BoxerScraperService, BoxingFightCardService
from sbtb.fighter.domain import RankDomain, FightCardDomain
from sbtb.fighter.repository import FighterRepo, RankRepo, FightOrganizationRepo, WeightClassRepo, FightCardRepo
from sbtb.fighter.scraper import BoxingRankScraper, BoxingFightCardScraper

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
async def scrape_and_save_boxing_ranks(scraper: BoxingRankScraper = Depends(get_boxing_scraper),
                                       fighter_repo: FighterRepo = Depends(get_boxer_repo),
                                       organization_repo: FightOrganizationRepo = Depends(get_boxer_org_repo),
                                       rank_repo: RankRepo = Depends(get_rank_repo),
                                       weight_class_repo: WeightClassRepo = Depends(get_weight_class_repo)
                                       ) -> Response:
    service = BoxerScraperService(scraper=scraper, fighter_repo=fighter_repo,
                                  organization_repo=organization_repo,
                                  rank_repo=rank_repo,
                                  weight_class_repo=weight_class_repo)
    updated_ranks: List[RankRead] = await service.scrape_and_update_boxing_ranks()
    return JSONResponse(
        content={"updated_ranks": jsonable_encoder(updated_ranks)},
        status_code=status.HTTP_200_OK,
    )


@router.get("/update-boxing-fight-cards",
            response_description="Update boxing fight cards",
            response_model=List[FightCardRead],
            tags=["fighters"])
async def scrape_and_save_boxing_fight_cards(scraper: BoxingFightCardScraper = Depends(get_boxing_fight_card_scraper),
                                             fighter_repo: FighterRepo = Depends(get_boxer_repo),
                                             weight_class_repo: WeightClassRepo = Depends(get_weight_class_repo),
                                             fight_card_repo: FightCardRepo = Depends(get_fight_card_repo)
                                             ) -> Response:
    service = BoxingFightCardService(scraper=scraper,
                                     fighter_repo=fighter_repo,
                                     weight_class_repo=weight_class_repo,
                                     fight_card_repo=fight_card_repo)
    updated_fight_cards: List[FightCardDomain] = await service.scrape_and_update_boxing_fight_cards()
    fight_card_reads = [FightCardRead.model_validate(fc) for fc in updated_fight_cards]
    return JSONResponse(
        content={"updated_boxing_fight_cards": jsonable_encoder(fight_card_reads)},
        status_code=status.HTTP_200_OK,
    )
