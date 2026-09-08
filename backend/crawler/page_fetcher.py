import time
from dataclasses import dataclass

import httpx


class FetchError(Exception):
    pass


@dataclass
class FetchResult:
    url: str
    status_code: int
    content: str
    content_type: str


class PageFetcher:
    def __init__(
        self,
        user_agent: str,
        timeout_seconds: int = 10,
    ):
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds

    def fetch(self, url: str) -> FetchResult:
        """
        Fetch an HTML/text page with retries.

        Hosted environments can experience transient connection resets
        or slow upstream responses. Retry a failed request before giving
        up, while keeping the crawler limited to text/HTML content.
        """

        headers = {
            "User-Agent": self.user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

        last_error = None

        for attempt in range(3):
            try:
                response = httpx.get(
                    url,
                    headers=headers,
                    timeout=20,
                    follow_redirects=True,
                    http2=False,
                )

                content_type = response.headers.get(
                    "content-type",
                    "",
                ).lower()

                if response.status_code >= 400:
                    raise FetchError(
                        f"Fetch {url} returned status "
                        f"{response.status_code}"
                    )

                if (
                    "text/html" not in content_type
                    and "text" not in content_type
                ):
                    raise FetchError(
                        f"Skipping non-text content at {url} "
                        f"({content_type})"
                    )

                return FetchResult(
                    url=str(response.url),
                    status_code=response.status_code,
                    content=response.text,
                    content_type=content_type,
                )

            except (httpx.HTTPError, FetchError) as exc:
                last_error = exc

                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                else:
                    raise FetchError(
                        f"Failed to fetch {url} after 3 attempts: "
                        f"{last_error}"
                    ) from exc

        raise FetchError(
            f"Failed to fetch {url}: {last_error}"
        )
