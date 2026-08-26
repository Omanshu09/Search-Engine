"""
Search engine orchestration.

This is ATLAS's "discover sources" pipeline: given a query, it (1) finds
candidate URLs via the crawler's lightweight seed discovery, (2) crawls and
indexes those pages into this process's in-memory index, (3) scores them
with BM25 (keyword) and, when available, semantic similarity, and
(4) blends both signals with the ranking engine to produce a final ordered
list. Search is intentionally query-scoped rather than backed by a
pre-built whole-web index, per the project's "don't build a whole-web
crawler" constraint -- each query does a small, targeted crawl of its own.
"""
import hashlib
import time
from typing import List

from backend.core.query_processor import QueryProcessor
from backend.core.ranking_engine import RankingEngine
from backend.crawler.crawler import Crawler
from backend.indexing.index_manager import IndexManager
from backend.ai.semantic_search import SemanticSearch
from backend.models.search_models import SearchRequest, SearchResponse, SearchResultItem
from backend.utils.text import truncate
from backend.utils.urls import get_domain
from backend.utils.logging import get_logger

logger = get_logger(__name__)


def _doc_id_for_url(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def _normalize_scores(scores: dict) -> dict:
    if not scores:
        return {}
    values = list(scores.values())
    lo, hi = min(values), max(values)
    if hi == lo:
        return {k: (1.0 if hi > 0 else 0.0) for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


class SearchEngine:
    def __init__(
        self,
        index_manager: IndexManager,
        query_processor: QueryProcessor,
        crawler: Crawler,
        semantic_search: SemanticSearch,
        ranking_engine: RankingEngine,
        seed_urls_per_query: int = 8,
        max_crawl_concurrency: int = 5,
    ):
        self.index_manager = index_manager
        self.query_processor = query_processor
        self.crawler = crawler
        self.semantic_search = semantic_search
        self.ranking_engine = ranking_engine
        self.seed_urls_per_query = seed_urls_per_query
        self.max_crawl_concurrency = max_crawl_concurrency

    def search(self, request: SearchRequest) -> SearchResponse:
        started = time.perf_counter()
        processed = self.query_processor.process(request.query)

        seed_urls = self.crawler.discover_seed_urls(processed.normalized_text, limit=self.seed_urls_per_query)
        pages = self.crawler.crawl_many(seed_urls, max_concurrency=self.max_crawl_concurrency)

        doc_ids: List[str] = []
        for page in pages:
            url = page.metadata.get("url", "")
            if not url:
                continue
            doc_id = _doc_id_for_url(url)
            self.index_manager.index_document(doc_id, url=url, title=page.title, text=page.text)
            doc_ids.append(doc_id)

        if not doc_ids:
            took_ms = (time.perf_counter() - started) * 1000
            return SearchResponse(query=request.query, results=[], total_results=0, took_ms=took_ms)

        bm25_ranked = self.index_manager.keyword_search(request.query, top_k=len(doc_ids))
        bm25_scores = dict(bm25_ranked) if bm25_ranked else {doc_id: 0.0 for doc_id in doc_ids}

        semantic_scores = {}
        if request.use_semantic_search:
            doc_vectors = self.index_manager.document_vectors(doc_ids)
            semantic_ranked = self.semantic_search.search(request.query, doc_vectors, top_k=len(doc_ids))
            semantic_scores = dict(semantic_ranked)

        bm25_norm = _normalize_scores(bm25_scores)
        semantic_norm = _normalize_scores(semantic_scores)

        candidates = [
            {
                "doc_id": doc_id,
                "bm25_score": bm25_norm.get(doc_id, 0.0),
                "semantic_score": semantic_norm.get(doc_id, 0.0),
            }
            for doc_id in doc_ids
        ]
        ranked = self.ranking_engine.rank(candidates)[: request.top_k]

        results: List[SearchResultItem] = []
        for candidate in ranked:
            doc = self.index_manager.get_document(candidate["doc_id"])
            if doc is None:
                continue
            results.append(
                SearchResultItem(
                    id=doc.doc_id,
                    title=doc.title,
                    url=doc.url,
                    snippet=truncate(doc.text, 280),
                    score=round(candidate["final_score"], 4),
                    source_domain=get_domain(doc.url),
                )
            )

        took_ms = (time.perf_counter() - started) * 1000
        return SearchResponse(query=request.query, results=results, total_results=len(results), took_ms=took_ms)
