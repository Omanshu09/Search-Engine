"""
Text tokenization for indexing and BM25 scoring.

This has a real, working baseline implementation (lowercase, strip
punctuation, split on whitespace, remove a small stopword list) since
tokenization quality directly affects retrieval quality and is cheap to
get right early.
"""
import re
from typing import List

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "is", "are", "was",
    "were", "be", "been", "being", "to", "of", "in", "on", "for", "with",
    "at", "by", "from", "as", "that", "this", "it", "its", "into", "than",
    "so", "such", "not", "no", "do", "does", "did", "can", "could", "will",
    "would", "should", "may", "might", "about", "over", "under",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class Tokenizer:
    def __init__(self, remove_stopwords: bool = True):
        self.remove_stopwords = remove_stopwords

    def tokenize(self, text: str) -> List[str]:
        """Lowercase, strip punctuation, split into word tokens."""
        tokens = _TOKEN_RE.findall(text.lower())
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in _STOPWORDS]
        return tokens
