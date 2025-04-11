from fastapi import Depends

from sbtb.database.session import DbSession
from sbtb.fighter.scraper import BoxingRankScraper, BoxingFightCardScraper
from sbtb.fighter.service import BoxerScraperService, BoxingFightCardService
from sbtb.fighter.repository import FighterRepo, FightOrganizationRepo, RankRepo, WeightClassRepo, FightCardRepo
from sbtb.fighter.driver import ChromeDriver


def get_boxing_scraper():
    return BoxingRankScraper()


def get_boxing_fight_card_scraper() -> BoxingFightCardScraper:
    chrome_driver = ChromeDriver()
    return BoxingFightCardScraper(driver=chrome_driver)


def get_boxer_repo(db: DbSession) -> FighterRepo:
    return FighterRepo(db=db)


def get_boxer_org_repo(db: DbSession) -> FightOrganizationRepo:
    return FightOrganizationRepo(db=db)


def get_rank_repo(db: DbSession) -> RankRepo:
    return RankRepo(db=db)


def get_weight_class_repo(db: DbSession) -> WeightClassRepo:
    return WeightClassRepo(db=db)


def get_fight_card_repo(db: DbSession) -> FightCardRepo:
    return FightCardRepo(db=db)


def get_boxer_scraper_service(
    scraper: BoxingRankScraper = Depends(get_boxing_scraper),
    fighter_repo: FighterRepo = Depends(get_boxer_repo),
    organization_repo: FightOrganizationRepo = Depends(get_boxer_org_repo),
    rank_repo: RankRepo = Depends(get_rank_repo),
    weight_class_repo: WeightClassRepo = Depends(get_weight_class_repo)
) -> BoxerScraperService:
    return BoxerScraperService(
        scraper=scraper,
        fighter_repo=fighter_repo,
        organization_repo=organization_repo,
        rank_repo=rank_repo,
        weight_class_repo=weight_class_repo
    )


def get_boxing_fight_card_service(
    scraper: BoxingFightCardScraper = Depends(get_boxing_fight_card_scraper),
    fighter_repo: FighterRepo = Depends(get_boxer_repo),
    weight_class_repo: WeightClassRepo = Depends(get_weight_class_repo),
    fight_card_repo: FightCardRepo = Depends(get_fight_card_repo),
) -> BoxingFightCardService:
    return BoxingFightCardService(
        scraper=scraper,
        fighter_repo=fighter_repo,
        weight_class_repo=weight_class_repo,
        fight_card_repo=fight_card_repo
    )
