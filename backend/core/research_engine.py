"""
Research engine orchestration.

Given a natural-language question, reuses search_engine.py's discovery +
crawl + index pipeline to gather sources, extracts claims from each source,
reconciles those claims across sources (evidence_engine.py), attaches
citations (citation_engine.py), and synthesizes a final cited answer
(ai/rag.py -- LLM-backed when configured, extractive fallback otherwise).
"""
import time
from typing import Dict, List

from backend.core.search_engine import SearchEngine
from backend.core.evidence_engine import EvidenceEngine
from backend.core.citation_engine import CitationEngine
from backend.ai.claim_extractor import ClaimExtractor
from backend.ai.rag import RAGSynthesizer
from backend.models.research_models import ResearchRequest, ResearchResponse
from backend.models.search_models import SearchRequest
from backend.models.source_models import SourceRef
from backend.utils.urls import get_domain
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class ResearchEngine:
    def __init__(
        self,
        search_engine: SearchEngine,
        claim_extractor: ClaimExtractor,
        evidence_engine: EvidenceEngine,
        citation_engine: CitationEngine,
        rag_synthesizer: RAGSynthesizer,
    ):
        self.search_engine = search_engine
        self.claim_extractor = claim_extractor
        self.evidence_engine = evidence_engine
        self.citation_engine = citation_engine
        self.rag_synthesizer = rag_synthesizer

    def research(self, request: ResearchRequest) -> ResearchResponse:
        started = time.perf_counter()

        search_response = self.search_engine.search(
            SearchRequest(query=request.question, top_k=request.max_sources, use_semantic_search=True)
        )

        sources_by_id: Dict[str, SourceRef] = {}
        claims_by_source: Dict[str, List[str]] = {}

        for result in search_response.results:
            source_ref = SourceRef(id=result.id, title=result.title, url=result.url, domain=result.source_domain)
            sources_by_id[result.id] = source_ref

            doc = self.search_engine.index_manager.get_document(result.id)
            source_text = doc.text if doc else result.snippet
            claims_by_source[result.id] = self.claim_extractor.extract(source_text)

        evidence = self.evidence_engine.evaluate(claims_by_source, sources_by_id)
        cited_sources = self.citation_engine.attach_citations(evidence)

        source_index_by_id = {source.id: i + 1 for i, source in enumerate(cited_sources)}
        rag_evidence = []
        for claim_evidence in evidence:
            for source in claim_evidence.supporting_sources:
                index = source_index_by_id.get(source.id)
                if index is not None:
                    rag_evidence.append({"claim": claim_evidence.claim, "source_index": index})
                    break  # one representative citation per claim is enough for the prompt

        answer = self.rag_synthesizer.synthesize(request.question, rag_evidence)

        took_ms = (time.perf_counter() - started) * 1000
        return ResearchResponse(
            question=request.question,
            answer=answer,
            claims=evidence,
            sources=cited_sources,
            took_ms=took_ms,
        )
