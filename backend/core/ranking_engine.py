"""
Ranking engine.

Combines BM25 keyword relevance with semantic similarity into a single
score. Both inputs are expected pre-normalized to a roughly comparable
scale by the caller (search_engine.py); this class just applies the
configured blend weight.
"""
from typing import List, Sequence


class RankingEngine:
    def __init__(self, semantic_weight: float = 0.4):
        self.semantic_weight = semantic_weight

    def rank(self, candidates: Sequence[dict]) -> List[dict]:
        """
        Each candidate dict is expected to have "bm25_score" and
        "semantic_score" (either may be 0.0 if that signal wasn't
        available). Adds a "final_score" key and returns candidates
        sorted descending by it.
        """
        scored = []
        for candidate in candidates:
            bm25 = candidate.get("bm25_score", 0.0)
            semantic = candidate.get("semantic_score", 0.0)
            final = (1 - self.semantic_weight) * bm25 + self.semantic_weight * semantic
            scored.append({**candidate, "final_score": final})
        return sorted(scored, key=lambda c: c["final_score"], reverse=True)
