from abc import ABC, abstractmethod
from typing import Any

import aiohttp
import bs4
import structlog

logger = structlog.get_logger(__name__)


class BaseScraper(ABC):
    URL: str
    HEADERS: dict

    @staticmethod
    def load_soup(html_source: str) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(html_source, "lxml")

    async def request_data(self) -> str | None:
        try:
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(self.URL, timeout=aiohttp.ClientTimeout(total=10)) as res:
                    res.raise_for_status()
                    return await res.text()
        except Exception:
            logger.exception(f"ERROR OCCURRED WHILE SCRAPING {self.__class__.__name__}")
        return None

    @abstractmethod
    async def run_scraper(self) -> list[Any]: ...

    @abstractmethod
    def parse(self, raw_data: Any) -> list[Any]: ...
