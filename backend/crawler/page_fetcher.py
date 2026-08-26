"""
HTTP fetching for the crawler.

Synchronous httpx client with timeouts, redirects, and a fixed User-Agent,
so crawler.py doesn't deal with transport concerns directly. Kept
synchronous (rather than async) so it can be called directly from FastAPI's
sync route handlers, which run in a threadpool.
"""
from dataclasses import dataclass

import httpx

from backend.utils.logging import get_logger

logger = get_logger(__name__)


class FetchError(Exception):
    """Raised when a page cannot be fetched."""


@dataclass
class FetchResult:
    url: str
    status_code: int
    content: str
    content_type: str


class PageFetcher:
    def __init__(self, user_agent: str, timeout_seconds: int = 10):
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds

    def fetch(self, url: str) -> FetchResult:
        try:
            response = httpx.get(
                url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout_seconds,
                follow_redirects=True,
            )
        except httpx.HTTPError as exc:
            raise FetchError(f"Failed to fetch {url}: {exc}") from exc

        content_type = response.headers.get("content-type", "")
        if response.status_code >= 400:
            raise FetchError(f"Fetch {url} returned status {response.status_code}")
        if "text/html" not in content_type and "text" not in content_type:
            raise FetchError(f"Skipping non-text content at {url} ({content_type})")

        return FetchResult(
            url=str(response.url),
            status_code=response.status_code,
            content=response.text,
            content_type=content_type,
        )
