import traceback
import logging
from typing import List, Dict, Optional

from sbtb.fighter.scraper import BoxingScraper
from sbtb.fighter.repository import FighterRepo, FightingOrganizationRepo, RankRepo, WeightClassRepo
from sbtb.fighter.schemas import FighterSchema, RawBoxerSchema, RankSchema

logger = logging.getLogger(__name__)


class BoxerScraperService:
    def __init__(self, scraper: BoxingScraper, fighter_repo: FighterRepo, organization_repo: FightingOrganizationRepo,
                 rank_repo: RankRepo, weight_class_repo: WeightClassRepo):
        self.scraper = scraper
        self.fighter_repo = fighter_repo
        self.organization_repo = organization_repo
        self.rank_repo = rank_repo
        self.weight_class_repo = weight_class_repo

    async def scrape_and_update_boxer_ranks(self) -> Optional[List[RankSchema]]:
        try:
            grouped_rankings: Dict[str, Dict[str, List[RawBoxerSchema]]] = await self.scraper.run_scraper()
            if not grouped_rankings:
                return None

            organizations = await self.organization_repo.get_all()
            weight_classes = await self.weight_class_repo.get_all()

            ranks_to_upsert = []
            for raw_weight_class, raw_organizations in grouped_rankings.items():
                for raw_organization, raw_boxers in raw_organizations.items():
                    for i, raw_boxer in enumerate(raw_boxers):
                        raw_fighter = FighterSchema(
                            name=raw_boxer.name
                        )
                        fighter = await self.fighter_repo.get_or_create(raw_fighter=raw_fighter)
                        if fighter is None:
                            logger.error(f"Failed to save fighter: {raw_fighter.name}")
                            continue

                        organization = next((org for org in organizations if org.name.value == raw_organization), None)
                        if organization is None:
                            logger.error(f"Organization not found: {raw_organization}")
                            continue

                        weight_class = next((wc for wc in weight_classes if wc.name == raw_weight_class), None)
                        if weight_class is None:
                            logger.error(f"Weight class not found: {raw_weight_class}")
                            continue

                        rank = RankSchema(
                            rank=raw_boxer.rank,
                            fighter_id=fighter.id,
                            weight_class_id=weight_class.id,
                            organization_id=organization.id
                        )
                        ranks_to_upsert.append(rank)

            saved_ranks = await self.rank_repo.bulk_upsert(ranks=ranks_to_upsert)
            logger.info(f"Updated {len(saved_ranks)} fighters")

            return ranks_to_upsert
        except Exception as e:
            logger.error(f"ERROR OCCURRED WHILE SCRAPING FIGHTERS {traceback.format_exc()}")
            return None
