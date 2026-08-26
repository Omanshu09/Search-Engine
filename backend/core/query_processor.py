"""
Query understanding and normalization.

Takes a raw user query and turns it into a structured form the rest of the
pipeline can use: cleaned text, detected intent (search vs. research),
extracted keywords/entities, and optional query expansion.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ProcessedQuery:
    raw_query: str
    normalized_text: str
    keywords: List[str] = field(default_factory=list)
    # TODO: entities, detected language, intent classification


class QueryProcessor:
    def process(self, raw_query: str) -> ProcessedQuery:
        """
        Normalize and tokenize a raw query.

        TODO: lowercase/strip, remove stopwords for keyword extraction
        (reuse indexing/tokenizer.py), and eventually detect intent and
        expand ambiguous queries.
        """
        normalized = raw_query.strip().lower()
        keywords = [w for w in normalized.split() if w]
        return ProcessedQuery(raw_query=raw_query, normalized_text=normalized, keywords=keywords)
