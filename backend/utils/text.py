"""Small reusable text utilities shared across indexing, crawling, and AI layers."""
import re


def clean_whitespace(text: str) -> str:
    """Collapse runs of whitespace into single spaces and strip ends."""
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, max_chars: int = 300, suffix: str = "...") -> str:
    """Truncate text to max_chars, adding suffix if it was cut."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)].rstrip() + suffix


def split_sentences(text: str) -> list[str]:
    """
    Naive sentence splitter (splits on '.', '!', '?' followed by whitespace).
    TODO: replace with a proper sentence tokenizer (e.g. spaCy or nltk)
    if/when accuracy matters more than zero extra dependencies.
    """
    text = clean_whitespace(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p for p in parts if p]
