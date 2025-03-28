from sbtb.database.session import DbSession
from sbtb.fighter.service import BoxerScraperService
from sbtb.fighter.scraper import BoxingScraper
from sbtb.fighter.repository import FighterRepo


async def get_boxer_scraper():
    return BoxingScraper()

async def get_boxer_repo(db: DbSession) -> FighterRepo:
    return FighterRepo(db=db)

async def get_boxer_scraper_service() -> BoxerScraperService:
    boxer_scraper = await get_boxer_scraper()
    repo = await get_boxer_repo(db=DbSession)
    return BoxerScraperService(scraper=boxer_scraper, repo=repo)
