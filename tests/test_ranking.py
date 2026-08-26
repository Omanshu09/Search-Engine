from backend.indexing.inverted_index import InvertedIndex
from backend.indexing.bm25 import BM25


def test_bm25_scores_relevant_doc_higher():
    index = InvertedIndex()
    index.add_document("doc1", ["atlas", "search", "engine"])
    index.add_document("doc2", ["unrelated", "content", "here"])
    bm25 = BM25(index)
    scores = dict(bm25.rank(["search"], ["doc1", "doc2"]))
    assert scores["doc1"] > scores["doc2"]
