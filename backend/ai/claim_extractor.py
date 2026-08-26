"""
Claim extraction.

Pulls discrete, checkable factual claims out of a source's text so
evidence_engine.py can compare claims across sources. Uses the LLM when
configured for higher-quality extraction; otherwise falls back to a
heuristic (sentences containing numbers, dates, or enough content words
tend to be checkable factual statements, unlike filler sentences).
"""
import re
from typing import List

from backend.ai.llm import LLMClient
from backend.utils.text import split_sentences

_NUMBER_OR_DATE_RE = re.compile(r"\d")


class ClaimExtractor:
    def __init__(self, llm_client: LLMClient | None = None, max_claims: int = 6):
        self.llm_client = llm_client
        self.max_claims = max_claims

    def extract(self, source_text: str) -> List[str]:
        if self.llm_client and self.llm_client.is_configured:
            return self._extract_with_llm(source_text)
        return self._extract_heuristic(source_text)

    def _extract_with_llm(self, source_text: str) -> List[str]:
        prompt = (
            "List the distinct, checkable factual claims made in the passage below. "
            "Return one claim per line, plain text, no numbering, no commentary. "
            f"Return at most {self.max_claims} claims.\n\nPassage:\n{source_text[:4000]}"
        )
        try:
            raw = self.llm_client.complete(prompt, max_tokens=500)
        except Exception:
            return self._extract_heuristic(source_text)
        claims = [line.strip("-* \t") for line in raw.splitlines() if line.strip()]
        return claims[: self.max_claims]

    def _extract_heuristic(self, source_text: str) -> List[str]:
        sentences = split_sentences(source_text)
        candidates = [
            s for s in sentences
            if _NUMBER_OR_DATE_RE.search(s) and 6 <= len(s.split()) <= 40
        ]
        if not candidates:
            candidates = [s for s in sentences if 6 <= len(s.split()) <= 40]
        return candidates[: self.max_claims]
