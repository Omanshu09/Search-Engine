"""
Document storage.

Persists the raw/cleaned text and metadata for each indexed document so
search results and citations can be resolved back to actual content.
In-memory placeholder now; swap for PostgreSQL/SQLite without changing
the interface.
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class StoredDocument:
    doc_id: str
    url: str
    title: str
    text: str
    metadata: dict


class DocumentStore:
    def __init__(self):
        self._docs: Dict[str, StoredDocument] = {}

    def save(self, document: StoredDocument) -> None:
        self._docs[document.doc_id] = document

    def get(self, doc_id: str) -> Optional[StoredDocument]:
        return self._docs.get(doc_id)

    def exists(self, doc_id: str) -> bool:
        return doc_id in self._docs
