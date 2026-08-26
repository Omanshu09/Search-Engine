"""
robots.txt compliance.

Fetches and caches robots.txt per domain and answers whether a given URL
is allowed to be crawled by ATLAS's user agent. Uses the stdlib
RobotFileParser for the actual matching logic.
"""
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from typing import Dict

import httpx

from backend.utils.logging import get_logger

logger = get_logger(__name__)


class RobotsChecker:
    def __init__(self, user_agent: str, timeout_seconds: int = 5):
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self._cache: Dict[str, RobotFileParser] = {}

    def _get_parser(self, url: str) -> RobotFileParser:
        parsed = urlparse(url)
        domain_key = f"{parsed.scheme}://{parsed.netloc}"
        if domain_key in self._cache:
            return self._cache[domain_key]

        parser = RobotFileParser()
        robots_url = f"{domain_key}/robots.txt"
        try:
            response = httpx.get(
                robots_url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout_seconds,
                follow_redirects=True,
            )
            if response.status_code == 200:
                parser.parse(response.text.splitlines())
            else:
                # No robots.txt (404, etc.) -> permissive by default.
                parser.parse([])
        except httpx.HTTPError:
            # Network failure fetching robots.txt: be permissive rather than
            # blocking crawls entirely, but log it so it's visible.
            logger.warning("Could not fetch robots.txt for %s; allowing by default", domain_key)
            parser.parse([])

        self._cache[domain_key] = parser
        return parser

    def is_allowed(self, url: str) -> bool:
        try:
            parser = self._get_parser(url)
            return parser.can_fetch(self.user_agent, url)
        except Exception:
            logger.warning("robots.txt check failed for %s; allowing by default", url)
            return True

    def crawl_delay(self, url: str) -> float:
        parser = self._get_parser(url)
        delay = parser.crawl_delay(self.user_agent)
        return float(delay) if delay else 0.0
