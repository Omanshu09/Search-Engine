"""
Evidence evaluation.

Groups claims that are effectively saying the same thing (across
different sources) into clusters, so ATLAS can report how many sources
agree vs. contradict on each point instead of just listing raw claims.
Clustering uses simple token-overlap (Jaccard) similarity, which is cheap,
dependency-free, and good enough for near-duplicate claim text; it can be
swapped for embedding-based clustering (ai/embeddings.py) later without
changing the interface.
"""
from typing import Dict, List

from backend.indexing.tokenizer import Tokenizer
from backend.models.research_models import ClaimEvidence
from backend.models.source_models import SourceRef

_SIMILARITY_THRESHOLD = 0.5


class EvidenceEngine:
    def __init__(self):
        self._tokenizer = Tokenizer(remove_stopwords=True)

    def _similarity(self, a: str, b: str) -> float:
        tokens_a, tokens_b = set(self._tokenizer.tokenize(a)), set(self._tokenizer.tokenize(b))
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return intersection / union if union else 0.0

    def evaluate(self, claims_by_source: Dict[str, List[str]], sources_by_id: Dict[str, SourceRef]) -> List[ClaimEvidence]:
        """
        `claims_by_source`: source_id -> list of claim strings.
        `sources_by_id`: source_id -> SourceRef, used to populate citations.
        """
        flat = [
            (source_id, claim)
            for source_id, claims in claims_by_source.items()
            for claim in claims
        ]

        clusters: List[List[tuple]] = []  # each cluster: list of (source_id, claim)
        for source_id, claim in flat:
            placed = False
            for cluster in clusters:
                if self._similarity(claim, cluster[0][1]) >= _SIMILARITY_THRESHOLD:
                    cluster.append((source_id, claim))
                    placed = True
                    break
            if not placed:
                clusters.append([(source_id, claim)])

        results: List[ClaimEvidence] = []
        for cluster in clusters:
            representative_claim = cluster[0][1]
            supporting_source_ids = {source_id for source_id, _ in cluster}
            supporting = [sources_by_id[sid] for sid in supporting_source_ids if sid in sources_by_id]
            confidence = len(supporting_source_ids) / max(len(claims_by_source), 1)
            results.append(
                ClaimEvidence(
                    claim=representative_claim,
                    supporting_sources=supporting,
                    contradicting_sources=[],  # TODO: detect negation/numeric conflict between clusters
                    confidence=round(confidence, 2),
                )
            )

        results.sort(key=lambda ce: ce.confidence or 0.0, reverse=True)
        return results
