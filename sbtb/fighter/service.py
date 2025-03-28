import traceback
import logging
from typing import List, Dict, Optional

from sbtb.fighter.scraper import BoxingScraper
from sbtb.fighter.repository import FighterRepo
from sbtb.fighter.schemas import FighterSchema, RawBoxerSchema

logger = logging.getLogger(__name__)

class BoxerScraperService:
    def __init__(self, scraper: BoxingScraper, repo: FighterRepo):
        self.scraper = scraper
        self.repo = repo

    async def scrape_and_save_fighters(self) -> Optional[List[FighterSchema]]:
        try:
            grouped_rankings: Dict[str, Dict[str, List[RawBoxerSchema]]] = await self.scraper.run_scraper()
            if not grouped_rankings:
                return None

            for weight_class, organizations in grouped_rankings.items():
                for organization, raw_boxers in organizations.items():
                    for raw_boxer in raw_boxers:
                        pass

        except Exception as e:
            logger.error(f"ERROR OCCURRED WHILE SCRAPING FIGHTERS {traceback.format_exc()}")
            return None
