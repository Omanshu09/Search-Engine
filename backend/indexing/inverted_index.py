"""
Inverted index: term -> list of (document_id, term_frequency) postings.

Baseline in-memory implementation. index_manager.py is responsible for
persistence; this class focuses purely on the data structure and lookups.
"""
from collections import defaultdict
from typing import Dict, List, Tuple


class InvertedIndex:
    def __init__(self):
        # term -> {doc_id: term_frequency}
        self._postings: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.doc_lengths: Dict[str, int] = {}
        self.total_docs: int = 0

    def add_document(self, doc_id: str, tokens: List[str]) -> None:
        term_counts: Dict[str, int] = defaultdict(int)
        for token in tokens:
            term_counts[token] += 1
        for term, count in term_counts.items():
            self._postings[term][doc_id] = count
        self.doc_lengths[doc_id] = len(tokens)
        self.total_docs += 1

    def get_postings(self, term: str) -> Dict[str, int]:
        return self._postings.get(term, {})

    def document_frequency(self, term: str) -> int:
        return len(self._postings.get(term, {}))

    def average_doc_length(self) -> float:
        if not self.doc_lengths:
            return 0.0
        return sum(self.doc_lengths.values()) / len(self.doc_lengths)
