from typing import List

from fastapi import Depends
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder

from sbtb.fighter.schemas import RankSchema
from sbtb.fighter.dependencies import get_boxer_repo, get_boxer_scraper, get_boxer_org_repo, get_rank_repo, \
    get_weight_class_repo
from sbtb.fighter.service import BoxerScraperService
from sbtb.fighter.repository import FighterRepo, RankRepo, FightingOrganizationRepo, WeightClassRepo
from sbtb.fighter.scraper import BoxingScraper

router = APIRouter(prefix="/fighter")


@router.get("/",
            response_description="Fighter Root",
            include_in_schema=False)
async def fighter_root() -> Response:
    return JSONResponse(
        content={"message": "Welcome to Fighter API"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/update-boxer-ranks",
            response_description="Scrape fighters",
            response_model=List[RankSchema],
            include_in_schema=False,
            tags=["fighters"])
async def scrape_and_save_boxer_ranks(scraper: BoxingScraper = Depends(get_boxer_scraper),
                                      fighter_repo: FighterRepo = Depends(get_boxer_repo),
                                      organization_repo: FightingOrganizationRepo = Depends(get_boxer_org_repo),
                                      rank_repo: RankRepo = Depends(get_rank_repo),
                                      weight_class_repo: WeightClassRepo = Depends(get_weight_class_repo)
                                      ) -> Response:
    service = BoxerScraperService(scraper=scraper, fighter_repo=fighter_repo,
                                  organization_repo=organization_repo,
                                  rank_repo=rank_repo,
                                  weight_class_repo=weight_class_repo)
    updated_ranks: List[RankSchema] = await service.scrape_and_update_boxer_ranks()
    return JSONResponse(
        content={"updated_ranks": jsonable_encoder(updated_ranks)},
        status_code=status.HTTP_200_OK,
    )
