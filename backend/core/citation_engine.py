"""
Citation engine.

Takes the ranked evidence clusters used to build an answer and produces
the ordered, de-duplicated list of sources actually cited, so the
frontend can render a numbered source list matching the [n] markers
the RAG synthesizer (or extractive fallback) put inline in the answer.
"""
from typing import List

from backend.models.research_models import ClaimEvidence
from backend.models.source_models import SourceRef


class CitationEngine:
    def attach_citations(self, evidence: List[ClaimEvidence]) -> List[SourceRef]:
        seen = set()
        ordered: List[SourceRef] = []
        for claim_evidence in evidence:
            for source in claim_evidence.supporting_sources:
                if source.id not in seen:
                    seen.add(source.id)
                    ordered.append(source)
        return ordered
