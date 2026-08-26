"""
BM25 ranking function over an InvertedIndex.

Standard Okapi BM25 implementation used as the keyword-relevance signal
that ranking_engine.py blends with semantic search scores.
"""
import math
from typing import Dict, List, Tuple

from backend.indexing.inverted_index import InvertedIndex


class BM25:
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.k1 = k1
        self.b = b

    def score(self, doc_id: str, query_terms: List[str]) -> float:
        avg_len = self.index.average_doc_length() or 1.0
        doc_len = self.index.doc_lengths.get(doc_id, 0)
        total_docs = self.index.total_docs or 1
        score = 0.0
        for term in query_terms:
            postings = self.index.get_postings(term)
            tf = postings.get(doc_id, 0)
            if tf == 0:
                continue
            df = self.index.document_frequency(term)
            idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / avg_len)
            score += idf * (numerator / denominator)
        return score

    def rank(self, query_terms: List[str], candidate_doc_ids: List[str]) -> List[Tuple[str, float]]:
        scored = [(doc_id, self.score(doc_id, query_terms)) for doc_id in candidate_doc_ids]
        return sorted(scored, key=lambda pair: pair[1], reverse=True)
