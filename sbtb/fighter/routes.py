from typing import List

from fastapi import Depends
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response

from sbtb.database.session import DbSession

from sbtb.fighter.schemas import FighterSchema
from sbtb.fighter.dependencies import get_boxer_scraper_service
from sbtb.fighter.service import BoxerScraperService


router = APIRouter(prefix="/fighter")

@router.get("/",
            response_description="Fighter Root",
            include_in_schema=False)
async def fighter_root() -> Response:
    return JSONResponse(
        content={"message": "Welcome to Fighter API"},
        status_code=status.HTTP_200_OK,
    )


# create fighter route (post)
@router.post("/",
             response_description="Create a new fighter",
             response_model=FighterSchema,
             status_code=status.HTTP_201_CREATED,
             tags=["fighters"])
async def create_fighter(fighter: FighterSchema, db: DbSession):
    pass


@router.get("/scrape-and-save",
            response_description="Scrape fighters",
            response_model=List[FighterSchema],
            include_in_schema=False,
            tags=["fighters"])
async def scrape_and_save_fighter(service: BoxerScraperService = Depends(get_boxer_scraper_service)) -> Response:
    boxers: List[FighterSchema] = await service.scrape_and_save_fighters()
    return JSONResponse(
        content=boxers,
        status_code=status.HTTP_200_OK,
    )
