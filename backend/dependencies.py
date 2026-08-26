"""
Shared dependency providers for FastAPI routes.

Anything expensive to construct (index manager, crawler, embedding/LLM
clients, engines) is created once per process and reused via these
dependency functions instead of being instantiated per-request.
"""
from functools import lru_cache

from backend.config import get_settings

from backend.crawler.url_manager import URLManager
from backend.crawler.robots import RobotsChecker
from backend.crawler.page_fetcher import PageFetcher
from backend.crawler.html_parser import HTMLParser
from backend.crawler.crawler import Crawler

from backend.ai.embeddings import EmbeddingClient
from backend.ai.semantic_search import SemanticSearch
from backend.ai.llm import LLMClient
from backend.ai.claim_extractor import ClaimExtractor
from backend.ai.rag import RAGSynthesizer

from backend.indexing.index_manager import IndexManager

from backend.core.query_processor import QueryProcessor
from backend.core.ranking_engine import RankingEngine
from backend.core.evidence_engine import EvidenceEngine
from backend.core.citation_engine import CitationEngine
from backend.core.search_engine import SearchEngine
from backend.core.research_engine import ResearchEngine


@lru_cache
def get_crawler() -> Crawler:
    settings = get_settings()
    return Crawler(
        url_manager=URLManager(),
        robots_checker=RobotsChecker(user_agent=settings.crawler_user_agent),
        page_fetcher=PageFetcher(
            user_agent=settings.crawler_user_agent,
            timeout_seconds=settings.crawler_request_timeout_seconds,
        ),
        html_parser=HTMLParser(),
    )


@lru_cache
def get_embedding_client() -> EmbeddingClient:
    settings = get_settings()
    return EmbeddingClient(model_name=settings.embedding_model_name, api_key=settings.llm_api_key)


@lru_cache
def get_semantic_search() -> SemanticSearch:
    return SemanticSearch(embedding_client=get_embedding_client())


@lru_cache
def get_llm_client() -> LLMClient:
    settings = get_settings()
    return LLMClient(provider=settings.llm_provider, api_key=settings.llm_api_key, model=settings.llm_model)


@lru_cache
def get_claim_extractor() -> ClaimExtractor:
    return ClaimExtractor(llm_client=get_llm_client())


@lru_cache
def get_rag_synthesizer() -> RAGSynthesizer:
    return RAGSynthesizer(llm_client=get_llm_client())


@lru_cache
def get_evidence_engine() -> EvidenceEngine:
    return EvidenceEngine()


@lru_cache
def get_citation_engine() -> CitationEngine:
    return CitationEngine()


@lru_cache
def get_index_manager() -> IndexManager:
    settings = get_settings()
    return IndexManager(storage_path=settings.index_storage_path, embedding_client=get_embedding_client())


@lru_cache
def get_query_processor() -> QueryProcessor:
    return QueryProcessor()


@lru_cache
def get_ranking_engine() -> RankingEngine:
    settings = get_settings()
    return RankingEngine(semantic_weight=settings.ranking_semantic_weight)


@lru_cache
def get_search_engine() -> SearchEngine:
    settings = get_settings()
    return SearchEngine(
        index_manager=get_index_manager(),
        query_processor=get_query_processor(),
        crawler=get_crawler(),
        semantic_search=get_semantic_search(),
        ranking_engine=get_ranking_engine(),
        seed_urls_per_query=settings.seed_urls_per_query,
        max_crawl_concurrency=settings.max_crawl_concurrency,
    )


@lru_cache
def get_research_engine() -> ResearchEngine:
    return ResearchEngine(
        search_engine=get_search_engine(),
        claim_extractor=get_claim_extractor(),
        evidence_engine=get_evidence_engine(),
        citation_engine=get_citation_engine(),
        rag_synthesizer=get_rag_synthesizer(),
    )
