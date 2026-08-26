"""
HTML content extraction.

Given raw HTML, extracts the page title, main readable text (with nav/
script/style/footer boilerplate stripped), and absolute outbound links.
"""
from dataclasses import dataclass, field
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from backend.utils.text import clean_whitespace

_BOILERPLATE_TAGS = ["script", "style", "nav", "footer", "header", "noscript", "form", "aside"]


@dataclass
class ParsedPage:
    title: str
    text: str
    links: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class HTMLParser:
    def parse(self, html: str, base_url: str) -> ParsedPage:
        soup = BeautifulSoup(html, "lxml")

        title_tag = soup.find("title")
        title = clean_whitespace(title_tag.get_text()) if title_tag else base_url

        for tag in soup.find_all(_BOILERPLATE_TAGS):
            tag.decompose()

        body = soup.find("body") or soup
        text = clean_whitespace(body.get_text(separator=" "))

        links: List[str] = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue
            links.append(urljoin(base_url, href))

        description_tag = soup.find("meta", attrs={"name": "description"})
        metadata = {}
        if description_tag and description_tag.get("content"):
            metadata["description"] = clean_whitespace(description_tag["content"])

        return ParsedPage(title=title, text=text, links=links, metadata=metadata)
