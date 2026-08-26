"""
Crawler orchestration.

Ties together url_manager.py (frontier), robots.py (policy), page_fetcher.py
(transport), and html_parser.py (extraction) into a polite crawler.

ATLAS does not run its own always-on, whole-web crawl (that would require
the "enormous infrastructure" the project spec explicitly says to avoid).
Instead, `discover_seed_urls` uses a lightweight web-search library purely
to find candidate URLs for a given query; ATLAS then does its own fetching,
parsing, indexing, and ranking of those pages. That keeps retrieval,
indexing, and ranking as ATLAS's own implementation while sidestepping the
need to build and host a general-purpose web crawler.
"""
from typing import List, Optional

from backend.crawler.url_manager import URLManager
from backend.crawler.robots import RobotsChecker
from backend.crawler.page_fetcher import PageFetcher, FetchError
from backend.crawler.html_parser import HTMLParser, ParsedPage
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class CrawledPage(ParsedPage):
    pass


class Crawler:
    def __init__(
        self,
        url_manager: URLManager,
        robots_checker: RobotsChecker,
        page_fetcher: PageFetcher,
        html_parser: HTMLParser,
    ):
        self.url_manager = url_manager
        self.robots_checker = robots_checker
        self.page_fetcher = page_fetcher
        self.html_parser = html_parser

    def discover_seed_urls(self, query: str, limit: int = 8) -> List[str]:
        """
        Find candidate URLs for a query using a lightweight web-search
        library (no API key required). This is the *only* place ATLAS
        leans on an external search provider -- purely for URL discovery,
        not for ranking or answer synthesis.
        """
        try:
            from ddgs import DDGS
        except ImportError:
            logger.error("ddgs is not installed; cannot discover seed URLs. pip install ddgs")
            return []

        urls: List[str] = []
        try:
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=limit):
                    url = result.get("href") or result.get("url")
                    if url:
                        urls.append(self.url_manager.normalize(url))
        except Exception as exc:
            logger.warning("Seed URL discovery failed for %r: %s", query, exc)
        return urls

    def crawl_url(self, url: str) -> Optional[CrawledPage]:
        """
        Fetch and parse a single URL, respecting robots.txt.
        Returns None (and logs) on any failure instead of raising, so a
        single bad source doesn't take down a whole search/research request.
        """
        normalized = self.url_manager.normalize(url)

        if not self.robots_checker.is_allowed(normalized):
            logger.info("Skipping %s: disallowed by robots.txt", normalized)
            return None

        try:
            fetched = self.page_fetcher.fetch(normalized)
        except FetchError as exc:
            logger.info("Skipping %s: %s", normalized, exc)
            return None

        try:
            parsed = self.html_parser.parse(fetched.content, base_url=fetched.url)
        except Exception as exc:
            logger.info("Failed to parse %s: %s", normalized, exc)
            return None

        if not parsed.text:
            return None

        return CrawledPage(title=parsed.title, text=parsed.text, links=parsed.links, metadata={
            **parsed.metadata,
            "url": fetched.url,
        })

    def crawl_many(self, urls: List[str], max_concurrency: int = 5) -> List[CrawledPage]:
        """Crawl a list of URLs concurrently (thread pool -- fetches are I/O bound), skipping failures."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        pages: List[CrawledPage] = []
        if not urls:
            return pages
        with ThreadPoolExecutor(max_workers=max(1, max_concurrency)) as executor:
            futures = {executor.submit(self.crawl_url, url): url for url in urls}
            for future in as_completed(futures):
                try:
                    page = future.result()
                except Exception as exc:
                    logger.info("Crawl task for %s raised: %s", futures[future], exc)
                    continue
                if page is not None:
                    pages.append(page)
        return pages
