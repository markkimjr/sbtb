import traceback
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

import bs4

from sbtb.core.config import settings
from sbtb.core.logging import logger
from sbtb.core.http_requests import get_request
from sbtb.fighter.schemas import WeightClassSchema, RawBoxerSchema


class BaseScraper(ABC):
    @staticmethod
    def load_soup(html_source: str) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(html_source, 'lxml')

    @abstractmethod
    async def run_scraper(self) -> List[Any]:
        pass

    @abstractmethod
    async def request_data(self) -> Optional[str]:
        pass

    @abstractmethod
    async def parse(self, raw_data: str) -> List[Any]:
        pass


class BoxingRankScraper(BaseScraper):
    URL = settings.BOXING_RANKINGS_URL
    HEADERS = settings.BOXING_HEADERS

    async def run_scraper(self) -> Optional[Dict[str, Dict[str, List[RawBoxerSchema]]]]:
        raw_data = await self.request_data()
        if not raw_data:
            return None
        return await self.parse(raw_data=raw_data)

    async def request_data(self) -> Optional[str]:
        try:
            res = get_request(url=self.URL, headers=self.HEADERS)
            if res.status_code == 200:
                html_source = res.text
                return html_source
        except Exception as e:
            logger.error(f"ERROR OCCURRED WHILE SCRAPING BOXING RANKINGS {traceback.format_exc()}")
        return None

    async def parse(self, raw_data: str) -> Dict[str, Dict[str, List[RawBoxerSchema]]]:
        parsed_rankings = {}
        soup = self.load_soup(html_source=raw_data)
        wrapper_div = soup.find("div", {"class": "card card-wrapper bg-black text-white p-2.5 md:p-5"})
        main_rankings_div = wrapper_div.find("div", recursive=False)
        section_divs = main_rankings_div.find_all("div", recursive=False)
        total_sections = len(section_divs)

        # divs alternate between weight class div (i.e. heavyweight) and rankings div (no parent-child relationship)
        # iterate total_sections//2 times to map weight class to rankings (process 2 divs at a time)
        current_idx = 0
        for i in range(total_sections // 2):
            division_div = section_divs[current_idx]
            rankings_div = section_divs[current_idx + 1]
            division_name_h3 = division_div.find("h3")
            division = division_name_h3.text.lower()
            pounds_str = division_div.find("span", {"class": "tex"}).text
            pounds = None

            # if division is heavyweight, pounds is None (200+)
            if division != "heavyweight":
                pounds = self.extract_pounds(pounds_str=pounds_str)

            weight_class = WeightClassSchema(
                name=division,
                pounds=pounds
            )

            logger.info(f"parsing weight class: {weight_class}")
            parsed_rankings[division] = self.parse_division(rankings_div=rankings_div)
            current_idx += 2

        return parsed_rankings

    def parse_division(self, rankings_div: bs4.element.Tag) -> Dict[str, List[RawBoxerSchema]]:
        grouped_rankings = {}
        organizations = rankings_div.find_all("div", recursive=False)
        for organization_div in organizations:
            organization_name = organization_div.find("h5").text.upper()
            main_rankings_div = organization_div.find("div", recursive=False)
            fighters = main_rankings_div.find_all("div", recursive=False)

            processed_fighters = []
            for i, fighter_div in enumerate(fighters):
                logger.info(f"parsing fighter {i+1}/{len(fighters)} for {organization_name}")
                raw_boxer = self.parse_fighter(fighter_div=fighter_div, idx=i)
                processed_fighters.extend(raw_boxer)
            grouped_rankings[organization_name] = processed_fighters

        return grouped_rankings

    def parse_fighter(self, fighter_div: bs4.element.Tag, idx: int) -> List[RawBoxerSchema]:
        name_container = fighter_div.find("div", recursive=False)
        if idx == 0:
            name_container = fighter_div

        name_span = name_container.find("span")

        # if there are 2 champions (i.e. champ + interim champion), return 2 fighters
        if name_span.find("br"):
            parts = [str(part).strip() for part in name_span.contents if part != "<br>"]
            primary_name = parts[0].lower()  # First part before <br>
            secondary_name = parts[2].lower()
            primary_champ = RawBoxerSchema(
                name=primary_name,
                rank=idx,
                is_champ=True
            )

            # remove any text after "(" in the secondary name
            if "(" in secondary_name:
                secondary_name = secondary_name.split("(")[0].strip()
            secondary_champ = RawBoxerSchema(
                name=secondary_name,
                rank=0.5,
                is_champ=True
            )
            return [primary_champ, secondary_champ]

        name_str = name_span.text
        name = name_str.split("(")[0].strip().lower()
        fighter = RawBoxerSchema(
            name=name,
            rank=idx,
            is_champ=True if idx == 0 else False
        )
        return [fighter]

    # if str = "175 lbs", return 175 (int)
    @staticmethod
    def extract_pounds(pounds_str: str) -> int:
        return int(pounds_str.split()[0])


class BoxingFightCardScraper(BaseScraper):
    URL = settings.BOXING_SCHEDULE_URL
    HEADERS = settings.BOXING_HEADERS

    async def run_scraper(self) -> Optional[Dict[str, Dict[str, List[RawBoxerSchema]]]]:
        raw_data = await self.request_data()
        if not raw_data:
            return None
        return await self.parse(raw_data=raw_data)

    async def request_data(self) -> Optional[str]:
        try:
            res = get_request(url=self.URL, headers=self.HEADERS)
            if res.status_code == 200:
                html_source = res.text
                return html_source
        except Exception as e:
            logger.error(f"ERROR OCCURRED WHILE SCRAPING BOXING SCHEDULE {traceback.format_exc()}")
        return None

    async def parse(self, raw_data: str):
        soup = self.load_soup(html_source=raw_data)
        script_tags = soup.find_all("script", type="application/ld+json")
        for script_tag in script_tags:
            script_text = script_tag.text.strip()
            if "Boxing Events" in script_text:
                pass
