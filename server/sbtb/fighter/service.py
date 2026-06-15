import structlog

from sbtb.core.database.session import DbSession
from sbtb.fighter.repository import (
    FeaturedFighterRepo,
    FightCardRepo,
    FighterRepo,
    FightOrganizationRepo,
    RankRepo,
    WeightClassRepo,
)
from sbtb.fighter.schemas import BoutInput, FeaturedFighterRead, ParsedFightCard, RankInput, RankRead
from sbtb.fighter.scraper import BoxingFightCardScraper, BoxingRankScraper
from sbtb.models import FightCard, Fighter
from sbtb.models.featured_fighter import FeaturedCollection

logger = structlog.get_logger(__name__)


class BoxerScraperService:
    def __init__(self, scraper: BoxingRankScraper):
        self.scraper = scraper

    async def scrape_and_update_boxing_ranks(self, session: DbSession) -> list[RankRead]:
        try:
            grouped_rankings = await self.scraper.run_scraper()
            if not grouped_rankings:
                return []

            fighter_repo = FighterRepo.from_session(session)
            organization_repo = FightOrganizationRepo.from_session(session)
            weight_class_repo = WeightClassRepo.from_session(session)
            rank_repo = RankRepo.from_session(session)

            organizations = await organization_repo.get_all(organization_repo.get_base_statement())
            weight_classes = await weight_class_repo.get_all(weight_class_repo.get_base_statement())

            rank_reads = []
            ranks_to_upsert = []
            for raw_weight_class, raw_organizations in grouped_rankings.items():
                for raw_organization, raw_boxers in raw_organizations.items():
                    for raw_boxer in raw_boxers:
                        fighter = await fighter_repo.get_or_create(name=raw_boxer.name)
                        if fighter is None:
                            logger.error(f"Failed to save fighter: {raw_boxer.name}")
                            continue

                        organization = next(
                            (org for org in organizations if org.name == raw_organization),
                            None,
                        )
                        if organization is None:
                            logger.error(f"Organization not found: {raw_organization}")
                            continue

                        weight_class = next((wc for wc in weight_classes if wc.name == raw_weight_class), None)
                        if weight_class is None:
                            logger.error(f"Weight class not found: {raw_weight_class}")
                            continue

                        ranks_to_upsert.append(
                            RankInput(
                                rank_type=raw_boxer.rank_type,
                                position=raw_boxer.position,
                                fighter_id=fighter.id,
                                weight_class_id=weight_class.id,
                                organization_id=organization.id,
                            )
                        )
                        rank_reads.append(
                            RankRead(
                                rank_type=raw_boxer.rank_type,
                                position=raw_boxer.position,
                                fighter_name=fighter.name,
                                organization_name=organization.name,
                                weight_class_name=weight_class.name,
                            )
                        )

            saved_ranks = await rank_repo.bulk_upsert(ranks=ranks_to_upsert)
            logger.info(f"Updated {len(saved_ranks)} boxing rankings")
            return rank_reads

        except Exception:
            logger.exception("ERROR OCCURRED WHILE SCRAPING BOXING RANKINGS")
            return []


class BoxingFightCardService:
    async def _get_or_create_fighter(self, fighter_repo: FighterRepo, name: str) -> Fighter | None:
        fighter = await fighter_repo.get_or_create(name=name.lower())
        if fighter is None:
            logger.error(f"Failed to save fighter: {name}")
        return fighter

    async def _build_bouts(
        self,
        fighter_repo: FighterRepo,
        title_fighters: list[str],
        undercard_fighters: list[str],
    ) -> list[BoutInput]:
        bouts = []

        # Title bout
        if len(title_fighters) == 2:
            red_corner = await self._get_or_create_fighter(fighter_repo, title_fighters[0])
            blue_corner = await self._get_or_create_fighter(fighter_repo, title_fighters[1])
            if red_corner and blue_corner:
                bouts.append(
                    BoutInput(
                        red_corner_id=red_corner.id,
                        blue_corner_id=blue_corner.id,
                        is_title_fight=True,
                        bout_order=1,
                    )
                )

        # Undercard bouts — flat list, paired as (red, blue)
        undercard_pairs = list(zip(undercard_fighters[::2], undercard_fighters[1::2]))
        for i, (red_name, blue_name) in enumerate(undercard_pairs):
            red_corner = await self._get_or_create_fighter(fighter_repo, red_name)
            blue_corner = await self._get_or_create_fighter(fighter_repo, blue_name)
            if red_corner and blue_corner:
                bouts.append(
                    BoutInput(
                        red_corner_id=red_corner.id,
                        blue_corner_id=blue_corner.id,
                        is_title_fight=False,
                        bout_order=i + 2,
                    )
                )

        return bouts

    async def scrape_and_update_boxing_fight_cards(self, session: DbSession) -> list[FightCard]:
        try:
            scraper = BoxingFightCardScraper()
            fighter_repo = FighterRepo.from_session(session)
            fight_card_repo = FightCardRepo.from_session(session)

            updated_fight_cards = []
            parsed_fight_cards: list[ParsedFightCard] | None = await scraper.run_scraper()
            if not parsed_fight_cards:
                return []

            for i, parsed_fight_card in enumerate(parsed_fight_cards):
                logger.info(f"Updating fight card {i + 1}/{len(parsed_fight_cards)}")
                title_fighters = parsed_fight_card.title_fighters
                undercard_fighters = parsed_fight_card.undercard_fighters

                fight_card = await fight_card_repo.get_or_create(
                    event_name=f"{title_fighters[0]} vs {title_fighters[1]}",
                    event_date=parsed_fight_card.fight_date,
                    location=parsed_fight_card.location,
                    network=parsed_fight_card.network,
                )

                bouts = await self._build_bouts(
                    fighter_repo=fighter_repo,
                    title_fighters=title_fighters,
                    undercard_fighters=undercard_fighters,
                )

                fight_card = await fight_card_repo.upsert_bouts(
                    fight_card=fight_card,
                    bouts=bouts,
                )
                updated_fight_cards.append(fight_card)

            logger.info(f"Updated {len(parsed_fight_cards)} boxing fight cards")
            return updated_fight_cards

        except Exception:
            logger.exception("ERROR OCCURRED WHILE SCRAPING BOXING FIGHT CARDS")
            return []


class FeaturedFighterService:
    async def get_by_collection(self, session: DbSession, collection: FeaturedCollection) -> list[FeaturedFighterRead]:
        repo = FeaturedFighterRepo.from_session(session)
        featured = await repo.get_by_collection(collection=collection)
        return [
            FeaturedFighterRead(
                id=entry.fighter.id,
                name=entry.fighter.name,
                avatar_url=entry.fighter.avatar_url,
            )
            for entry in featured
        ]


boxer_scraper_service = BoxerScraperService(scraper=BoxingRankScraper())
boxing_fight_card_service = BoxingFightCardService()
featured_fighter_service = FeaturedFighterService()
