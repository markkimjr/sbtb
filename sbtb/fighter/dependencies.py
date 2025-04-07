from sbtb.database.session import DbSession
from sbtb.fighter.scraper import BoxingRankScraper, BoxingFightCardScraper
from sbtb.fighter.repository import FighterRepo, FightingOrganizationRepo, RankRepo, WeightClassRepo, FightCardRepo
from sbtb.fighter.driver import ChromeDriver


async def get_boxing_scraper():
    return BoxingRankScraper()


async def get_boxing_fight_card_scraper() -> BoxingFightCardScraper:
    chrome_driver = ChromeDriver()
    return BoxingFightCardScraper(driver=chrome_driver)


async def get_boxer_repo(db: DbSession) -> FighterRepo:
    return FighterRepo(db=db)


async def get_boxer_org_repo(db: DbSession) -> FightingOrganizationRepo:
    return FightingOrganizationRepo(db=db)


async def get_rank_repo(db: DbSession) -> RankRepo:
    return RankRepo(db=db)


async def get_weight_class_repo(db: DbSession) -> WeightClassRepo:
    return WeightClassRepo(db=db)


async def get_fight_card_repo(db: DbSession) -> FightCardRepo:
    return FightCardRepo(db=db)