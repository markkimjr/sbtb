import datetime
import json
import re
from urllib.parse import urlparse

import aiohttp
import pytz
import structlog

from sbtb.core.config import settings
from sbtb.fighter.schemas import ParsedFightCard
from sbtb.fighter.scraper.base import BaseScraper

logger = structlog.get_logger(__name__)


class BoxingFightCardScraper(BaseScraper):
    URL = settings.BOXING_SCHEDULE_URL
    HEADERS = settings.BOXING_HEADERS
    PAGE_SIZE = 10

    # Pattern to find the schedule page JS chunk in HTML
    _CHUNK_URL_PATTERN = re.compile(r"/_next/static/chunks/app/schedule/page-[a-f0-9]+\.js")
    # Pattern to extract the Server Action ID from the chunk
    _ACTION_ID_PATTERN = re.compile(r'createServerReference\)?[^"]*"([a-f0-9]+)"')

    # EST/EDT/CST etc. → pytz timezone name
    _TIMEZONE_MAP = {
        "EST": "US/Eastern",
        "EDT": "US/Eastern",
        "CST": "US/Central",
        "CDT": "US/Central",
        "MST": "US/Mountain",
        "MDT": "US/Mountain",
        "PST": "US/Pacific",
        "PDT": "US/Pacific",
        "GMT": "UTC",
        "UTC": "UTC",
    }

    async def run_scraper(self) -> list[ParsedFightCard] | None:
        action_id = await self._discover_action_id()
        if not action_id:
            return None
        events = await self._fetch_all_events(action_id=action_id)
        if not events:
            return None
        return self.parse(raw_data=events)

    async def _discover_action_id(self) -> str | None:
        """Fetch the schedule page and extract the Server Action ID from its JS chunk."""
        html = await self.request_data()
        if not html:
            return None

        chunk_match = self._CHUNK_URL_PATTERN.search(html)
        if not chunk_match:
            logger.error("Schedule JS chunk URL not found in page HTML")
            return None

        parsed = urlparse(self.URL)
        chunk_url = f"{parsed.scheme}://{parsed.netloc}{chunk_match.group(0)}"

        try:
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(chunk_url, timeout=aiohttp.ClientTimeout(total=10)) as res:
                    res.raise_for_status()
                    chunk_text = await res.text()
        except Exception:
            logger.exception("Failed to fetch JS chunk")
            return None

        action_match = self._ACTION_ID_PATTERN.search(chunk_text)
        if not action_match:
            logger.error("Server Action ID not found in JS chunk")
            return None

        action_id = action_match.group(1)
        logger.info(f"Discovered Server Action ID: {action_id}")
        return action_id

    async def _fetch_all_events(self, action_id: str) -> list[dict] | None:
        """Paginate through all upcoming events via the Next.js Server Action."""
        all_events: list[dict] = []
        last_event_id = 0
        last_event_date = "2000-01-01T00:00:00"

        while True:
            payload = [
                "get_upcoming_events",
                {"last_event_id": last_event_id, "last_event_date": last_event_date},
                True,
                self.PAGE_SIZE,
            ]
            try:
                async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                    async with session.post(
                        self.URL,
                        headers={"Accept": "text/x-component", "next-action": action_id},
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=15),
                    ) as res:
                        res.raise_for_status()
                        text = await res.text()
            except Exception:
                logger.exception("Server Action POST failed")
                break

            results = self._extract_results(rsc_text=text)
            if not results:
                break

            all_events.extend(results)
            logger.info(f"Fetched {len(all_events)} fight cards so far")

            if len(results) < self.PAGE_SIZE:
                break

            last = results[-1]
            last_event_id = last["id"]
            last_event_date = f"{last['event_date']}T{last.get('event_time', '00:00:00')}"

        return all_events or None

    @staticmethod
    def _extract_results(rsc_text: str) -> list[dict] | None:
        """Parse the results list from the RSC Server Action payload."""
        for line in rsc_text.split("\n"):
            if '"results"' not in line:
                continue
            colon_idx = line.index(":")
            try:
                data = json.loads(line[colon_idx + 1 :])
                return data.get("results")
            except (json.JSONDecodeError, ValueError):
                continue
        return None

    def parse(self, raw_data: list[dict]) -> list[ParsedFightCard]:
        parsed = []
        for i, event in enumerate(raw_data):
            try:
                fight_card = self._parse_event(event=event)
                if fight_card:
                    parsed.append(fight_card)
                    logger.info(f"parsed fight card {i + 1}/{len(raw_data)}: {fight_card.title_fighters}")
            except Exception:
                logger.exception(f"Failed to parse event {event.get('id')}")
        return parsed

    def _parse_event(self, event: dict) -> ParsedFightCard | None:
        fights = event.get("fights", [])
        if not fights:
            return None

        main_event = next((f for f in fights if f.get("event_fight_type") == "Main Event"), None)
        if not main_event:
            return None

        title_fighters = [main_event["fighter1_name"], main_event["fighter2_name"]]
        undercard_fighters = [
            name
            for f in fights
            if f.get("event_fight_type") != "Main Event"
            for name in (f["fighter1_name"], f["fighter2_name"])
        ]

        fight_date_utc = self._parse_event_date(event=event)
        location = event.get("venue", {}).get("region_display_name", "")
        networks = event.get("networks", [])
        network = networks[0]["name"] if networks else None

        return ParsedFightCard(
            fight_date=fight_date_utc,
            title_fighters=title_fighters,
            undercard_fighters=undercard_fighters,
            location=location,
            network=network,
        )

    def _parse_event_date(self, event: dict) -> datetime.datetime:
        event_date = event["event_date"]  # "2026-06-05"
        event_time = event.get("event_time", "00:00:00")  # "17:30:00"
        timezone_str = event.get("event_timezone", "EST")
        naive_dt = datetime.datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M:%S")
        tz = pytz.timezone(self._TIMEZONE_MAP.get(timezone_str, "US/Eastern"))
        return tz.localize(naive_dt).astimezone(pytz.utc)
