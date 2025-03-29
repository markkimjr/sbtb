from sbtb.database.session import DbSession
from sbtb.fighter.scraper import BoxingScraper
from sbtb.fighter.repository import FighterRepo, FightingOrganizationRepo, RankRepo, WeightClassRepo


async def get_boxer_scraper():
    return BoxingScraper()


async def get_boxer_repo(db: DbSession) -> FighterRepo:
    return FighterRepo(db=db)


async def get_boxer_org_repo(db: DbSession) -> FightingOrganizationRepo:
    return FightingOrganizationRepo(db=db)


async def get_rank_repo(db: DbSession) -> RankRepo:
    return RankRepo(db=db)


async def get_weight_class_repo(db: DbSession) -> WeightClassRepo:
    return WeightClassRepo(db=db)
