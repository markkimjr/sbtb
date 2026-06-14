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

        # Main container holds weight-class headers and rankings divs as direct children.
        # There are multiple div.relative.flex.flex-col on the page; find the one that
        # actually contains weight-class h3 headers (class "font-medium").
        main_container = None
        for candidate in soup.select("div.relative.flex.flex-col"):
            if candidate.find("h3", class_="font-medium"):
                main_container = candidate
                break

        if main_container is None:
            # Log all hidden div IDs and the top-level div classes to help diagnose structure changes
            hidden_ids = [d.get("id") for d in soup.find_all("div", attrs={"hidden": True})]
            top_divs = (
                [d.get("class") for d in soup.find("body").find_all("div", recursive=False)][:5]
                if soup.find("body")
                else []
            )
            logger.error(f"main_container not found. Hidden div IDs: {hidden_ids}. Top-level body divs: {top_divs}")
            return {}
        section_divs = main_container.find_all("div", recursive=False)

        i = 0
        while i < len(section_divs) - 1:
            division_div = section_divs[i]
            division_name_h3 = division_div.find("h3", recursive=False)
            if division_name_h3 is None:
                i += 1
                continue

            rankings_div = section_divs[i + 1]
            division = division_name_h3.text.lower()
            pounds_span = division_div.find("span")
            pounds = None

            # if division is heavyweight, pounds is None (200+)
            if division != "heavyweight" and pounds_span:
                pounds = self.extract_pounds(pounds_str=pounds_span.text)

            logger.info(f"parsing weight class: {division} ({pounds} lbs)")
            parsed_rankings[division] = self.parse_division(rankings_div=rankings_div)
            i += 2

        return parsed_rankings

    def parse_division(self, rankings_div: bs4.element.Tag) -> dict[str, list[RawBoxerSchema]]:
        grouped_rankings = {}
        # rankings_div wraps an inner orgs container (flex-row div with 4 org columns)
        orgs_container = rankings_div.find("div", recursive=False)
        organizations = orgs_container.find_all("div", recursive=False)
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

    # if str = "175lbs" or "175 lbs", return 175 (int)
    @staticmethod
    def extract_pounds(pounds_str: str) -> int:
        return int("".join(c for c in pounds_str if c.isdigit()))
