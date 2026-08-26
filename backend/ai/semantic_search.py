"""
Semantic (vector) search.

Compares a query embedding against a set of candidate document embeddings
(passed in by the caller -- index_manager.py owns the actual vector
storage) using cosine similarity.
"""
from typing import Dict, List, Tuple

from backend.ai.embeddings import EmbeddingClient, cosine_similarity


class SemanticSearch:
    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client

    def search(
        self, query: str, doc_vectors: Dict[str, List[float]], top_k: int = 10
    ) -> List[Tuple[str, float]]:
        if not doc_vectors:
            return []
        query_vector = self.embedding_client.embed(query)
        scored = [
            (doc_id, cosine_similarity(query_vector, vector))
            for doc_id, vector in doc_vectors.items()
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]
