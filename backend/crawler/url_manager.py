"""
URL frontier management.

Tracks which URLs have been discovered, fetched, or are queued, avoids
re-crawling duplicates, and normalizes URLs (strip tracking params,
resolve relative links, dedupe trailing slashes, etc.).
"""
from typing import Set
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "ref", "ref_src",
}


class URLManager:
    def __init__(self):
        self._seen: Set[str] = set()
        self._queue: list[str] = []

    def normalize(self, url: str, base_url: str | None = None) -> str:
        """Resolve relative URLs, strip fragments/tracking params, lowercase host."""
        resolved = urljoin(base_url, url) if base_url else url
        parsed = urlparse(resolved)
        query_pairs = [
            (k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k.lower() not in _TRACKING_PARAMS
        ]
        netloc = parsed.netloc.lower()
        return urlunparse(parsed._replace(netloc=netloc, query=urlencode(query_pairs), fragment=""))

    def enqueue(self, url: str) -> bool:
        """Add a URL to the crawl queue if not already seen. Returns True if enqueued."""
        if url in self._seen:
            return False
        self._seen.add(url)
        self._queue.append(url)
        return True

    def next_url(self) -> str | None:
        return self._queue.pop(0) if self._queue else None
