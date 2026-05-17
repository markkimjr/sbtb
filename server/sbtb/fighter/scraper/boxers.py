import bs4
import structlog

from sbtb.core.config import settings
from sbtb.fighter.schemas import RawBoxerSchema
from sbtb.fighter.scraper.base import BaseScraper
from sbtb.models.rank import RankType

logger = structlog.get_logger(__name__)


class BoxingRankScraper(BaseScraper):
    URL = settings.BOXING_RANKINGS_URL
    HEADERS = settings.BOXING_HEADERS

    async def run_scraper(self) -> dict[str, dict[str, list[RawBoxerSchema]]] | None:
        raw_data = await self.request_data()
        if not raw_data:
            return None
        return self.parse(raw_data=raw_data)

    def parse(self, raw_data: str) -> dict[str, dict[str, list[RawBoxerSchema]]]:
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

            logger.info(f"parsing weight class: {division} ({pounds} lbs)")
            parsed_rankings[division] = self.parse_division(rankings_div=rankings_div)
            current_idx += 2

        return parsed_rankings

    def parse_division(self, rankings_div: bs4.element.Tag) -> dict[str, list[RawBoxerSchema]]:
        grouped_rankings = {}
        organizations = rankings_div.find_all("div", recursive=False)
        for organization_div in organizations:
            organization_name = organization_div.find("h5").text.upper()
            main_rankings_div = organization_div.find("div", recursive=False)
            fighters = main_rankings_div.find_all("div", recursive=False)

            processed_fighters = []
            for i, fighter_div in enumerate(fighters):
                logger.info(f"parsing fighter {i + 1}/{len(fighters)} for {organization_name}")
                raw_boxer = self.parse_fighter(fighter_div=fighter_div, idx=i)
                processed_fighters.extend(raw_boxer)
            grouped_rankings[organization_name] = processed_fighters

        return grouped_rankings

    def parse_fighter(self, fighter_div: bs4.element.Tag, idx: int) -> list[RawBoxerSchema]:
        name_container = fighter_div if idx == 0 else fighter_div.find("div", recursive=False)
        if name_container is None:
            return []

        name_span = name_container.find("span")
        if name_span is None:
            return []

        raw_text = name_span.get_text(strip=True)

        # Skip vacant positions and unrated slots
        if raw_text.upper() in ("VACANT", "NOT RATED", ""):
            return []

        # Dual champions in one slot: <a>Primary</a><br><a>Secondary (interim)</a>
        if name_span.find("br"):
            links = name_span.find_all("a")
            if not links:
                return []
            primary_name = links[0].get_text(strip=True).lower().split("(")[0].strip()
            results = [RawBoxerSchema(name=primary_name, rank_type=RankType.champion)]
            if len(links) > 1:
                secondary_text = links[1].get_text(strip=True).lower()
                secondary_name = secondary_text.split("(")[0].strip()
                if secondary_name:
                    results.append(RawBoxerSchema(name=secondary_name, rank_type=RankType.interim_champion))
            return results

        # Single fighter — detect rank type from parenthetical designation
        lower = raw_text.lower()
        name = lower.split("(")[0].strip()

        if "(champion in recess)" in lower:
            return [RawBoxerSchema(name=name, rank_type=RankType.champion_in_recess)]

        if "(interim)" in lower:
            return [RawBoxerSchema(name=name, rank_type=RankType.interim_champion)]

        if idx == 0:
            return [RawBoxerSchema(name=name, rank_type=RankType.champion)]

        # idx corresponds to actual position (1–15) since VACANT/NOT RATED divs
        # are still enumerated, preserving correct position numbers
        return [RawBoxerSchema(name=name, rank_type=RankType.contender, position=idx)]

    # if str = "175 lbs", return 175 (int)
    @staticmethod
    def extract_pounds(pounds_str: str) -> int:
        return int(pounds_str.split()[0])
