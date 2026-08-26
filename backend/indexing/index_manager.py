"""
Index manager.

Public entry point for the indexing subsystem: ties tokenizer, inverted
index, BM25, document store, and (optionally) embeddings together. This
in-memory version rebuilds its index per process; index_storage_path is
reserved for future persistence (see load()/persist()).
"""
from typing import Dict, List, Optional, Tuple

from backend.indexing.tokenizer import Tokenizer
from backend.indexing.inverted_index import InvertedIndex
from backend.indexing.bm25 import BM25
from backend.indexing.document_store import DocumentStore, StoredDocument
from backend.ai.embeddings import EmbeddingClient


class IndexManager:
    def __init__(self, storage_path: str, embedding_client: Optional[EmbeddingClient] = None):
        self.storage_path = storage_path
        self.tokenizer = Tokenizer()
        self.inverted_index = InvertedIndex()
        self.document_store = DocumentStore()
        self.bm25 = BM25(self.inverted_index)
        self.embedding_client = embedding_client
        self._embeddings: Dict[str, List[float]] = {}

    def index_document(self, doc_id: str, url: str, title: str, text: str, metadata: dict | None = None) -> None:
        if self.document_store.exists(doc_id):
            return  # already indexed this run
        tokens = self.tokenizer.tokenize(text)
        self.inverted_index.add_document(doc_id, tokens)
        self.document_store.save(
            StoredDocument(doc_id=doc_id, url=url, title=title, text=text, metadata=metadata or {})
        )
        if self.embedding_client is not None:
            # Embed a bounded prefix -- full-page embedding isn't needed for
            # relevance ranking and keeps this cheap for the hashing fallback too.
            self._embeddings[doc_id] = self.embedding_client.embed(text[:2000])

    def keyword_search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        query_terms = self.tokenizer.tokenize(query)
        candidate_ids = set()
        for term in query_terms:
            candidate_ids.update(self.inverted_index.get_postings(term).keys())
        ranked = self.bm25.rank(query_terms, list(candidate_ids))
        return ranked[:top_k]

    def document_vectors(self, doc_ids: List[str]) -> Dict[str, List[float]]:
        return {doc_id: self._embeddings[doc_id] for doc_id in doc_ids if doc_id in self._embeddings}

    def get_document(self, doc_id: str) -> Optional[StoredDocument]:
        return self.document_store.get(doc_id)

    def load(self) -> None:
        """TODO: load persisted index/doc store from self.storage_path."""
        pass

    def persist(self) -> None:
        """TODO: write index/doc store to self.storage_path."""
        pass
