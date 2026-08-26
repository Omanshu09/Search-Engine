from backend.ai.claim_extractor import ClaimExtractor
from backend.core.evidence_engine import EvidenceEngine
from backend.core.citation_engine import CitationEngine
from backend.ai.rag import RAGSynthesizer
from backend.ai.llm import LLMClient
from backend.models.source_models import SourceRef


def test_claim_extractor_heuristic_finds_numeric_sentences():
    extractor = ClaimExtractor(llm_client=None)
    text = "This is filler. The company was founded in 1998. More filler text here."
    claims = extractor.extract(text)
    assert any("1998" in c for c in claims)


def test_evidence_engine_clusters_similar_claims_and_counts_agreement():
    engine = EvidenceEngine()
    sources = {
        "s1": SourceRef(id="s1", title="A", url="https://a.example"),
        "s2": SourceRef(id="s2", title="B", url="https://b.example"),
    }
    claims_by_source = {
        "s1": ["The bridge was built in 1932."],
        "s2": ["The bridge was built in 1932 after years of planning."],
    }
    evidence = engine.evaluate(claims_by_source, sources)
    assert len(evidence) == 1
    assert len(evidence[0].supporting_sources) == 2


def test_citation_engine_dedupes_sources_in_order():
    from backend.models.research_models import ClaimEvidence

    s1 = SourceRef(id="s1", title="A", url="https://a.example")
    s2 = SourceRef(id="s2", title="B", url="https://b.example")
    evidence = [
        ClaimEvidence(claim="X", supporting_sources=[s1, s2]),
        ClaimEvidence(claim="Y", supporting_sources=[s1]),
    ]
    ordered = CitationEngine().attach_citations(evidence)
    assert [s.id for s in ordered] == ["s1", "s2"]


def test_rag_synthesizer_extractive_fallback_without_llm():
    synth = RAGSynthesizer(llm_client=LLMClient())  # no provider/key -> not configured
    answer = synth.synthesize("What happened?", [{"claim": "The bridge opened in 1932.", "source_index": 1}])
    assert "1932" in answer
