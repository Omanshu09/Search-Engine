from backend.indexing.inverted_index import InvertedIndex


def test_add_document_and_lookup():
    index = InvertedIndex()
    index.add_document("doc1", ["atlas", "search", "engine", "search"])
    postings = index.get_postings("search")
    assert postings == {"doc1": 2}
    assert index.document_frequency("atlas") == 1
    assert index.doc_lengths["doc1"] == 4
