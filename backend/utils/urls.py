"""URL helper utilities shared by the crawler and search layers."""
from urllib.parse import urlparse


def get_domain(url: str) -> str:
    """Return the network location (domain) of a URL, without scheme or path."""
    return urlparse(url).netloc.lower()


def is_valid_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False
