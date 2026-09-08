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
        user_agent: str,
        request_timeout_seconds: int = 10,
        robots_timeout_seconds: int = 5,
    ):
        self.url_manager = URLManager()
        self.robots_checker = RobotsChecker(
            user_agent=user_agent,
            timeout_seconds=robots_timeout_seconds,
        )
        self.page_fetcher = PageFetcher(
            user_agent=user_agent,
            timeout_seconds=request_timeout_seconds,
        )
        self.html_parser = HTMLParser()

    def discover_seed_urls(self, query: str, limit: int = 8) -> List[str]:
        """
        Discover search-result URLs using DDGS.

        Uses explicit mainstream search backends instead of DDGS's
        automatic backend selection. This prevents a single backend such
        as Wikipedia/Grokipedia from disproportionately determining the
        seed set, which is especially important on hosted environments.
        """
        try:
            from ddgs import DDGS
        except ImportError:
            logger.error(
                "ddgs is not installed; cannot discover seed URLs. "
                "pip install ddgs"
            )
            return []

        urls: List[str] = []

        try:
            with DDGS(timeout=15) as ddgs:
                results = ddgs.text(
                    query,
                    max_results=limit,
                    backend="google,bing,duckduckgo,brave",
                )

                for result in results:
                    url = result.get("href") or result.get("url")

                    if not url:
                        continue

                    normalized = self.url_manager.normalize(url)

                    if normalized and normalized not in urls:
                        urls.append(normalized)

                    if len(urls) >= limit:
                        break

        except Exception as exc:
            logger.warning(
                "Seed URL discovery failed for %r: %s",
                query,
                exc,
            )

        logger.info(
            "Discovered %d seed URLs for query %r",
            len(urls),
            query,
        )

        return urls

    def crawl_url(self, url: str) -> Optional[CrawledPage]:
        normalized = self.url_manager.normalize(url)

        if not self.robots_checker.is_allowed(normalized):
            logger.info(
                "Skipping %s: disallowed by robots.txt",
                normalized,
            )
            return None

        try:
            fetched = self.page_fetcher.fetch(normalized)
        except FetchError as exc:
            logger.info(
                "Skipping %s: %s",
                normalized,
                exc,
            )
            return None

        try:
            parsed = self.html_parser.parse(
                fetched.content,
                base_url=fetched.url,
            )
        except Exception as exc:
            logger.info(
                "Failed to parse %s: %s",
                normalized,
                exc,
            )
            return None

        if not parsed.text:
            logger.info(
                "Skipping %s: page contains no extracted text",
                normalized,
            )
            return None

        return CrawledPage(
            title=parsed.title,
            text=parsed.text,
            links=parsed.links,
            metadata={
                **parsed.metadata,
                "url": fetched.url,
            },
        )

    def crawl_many(
        self,
        urls: List[str],
        max_concurrency: int = 5,
    ) -> List[CrawledPage]:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        pages: List[CrawledPage] = []

        if not urls:
            return pages

        with ThreadPoolExecutor(
            max_workers=max(1, max_concurrency)
        ) as executor:
            futures = {
                executor.submit(self.crawl_url, url): url
                for url in urls
            }

            for future in as_completed(futures):
                url = futures[future]

                try:
                    page = future.result()
                except Exception as exc:
                    logger.info(
                        "Crawl task for %s raised: %s",
                        url,
                        exc,
                    )
                    continue

                if page is not None:
                    pages.append(page)

        logger.info(
            "Successfully crawled %d of %d seed URLs",
            len(pages),
            len(urls),
        )

        return pages
