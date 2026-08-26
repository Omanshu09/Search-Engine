from backend.ai.embeddings import EmbeddingClient, cosine_similarity
from backend.ai.semantic_search import SemanticSearch
from backend.core.ranking_engine import RankingEngine


def test_hashing_embedding_is_deterministic_and_normalized():
    client = EmbeddingClient()  # no model_name -> local hashing fallback
    v1 = client.embed("atlas search engine")
    v2 = client.embed("atlas search engine")
    assert v1 == v2
    norm = sum(x * x for x in v1) ** 0.5
    assert abs(norm - 1.0) < 1e-6 or norm == 0.0


def test_semantic_search_ranks_similar_text_higher():
    client = EmbeddingClient()
    semantic = SemanticSearch(embedding_client=client)
    doc_vectors = {
        "relevant": client.embed("atlas web research evidence engine"),
        "unrelated": client.embed("banana bread recipe instructions"),
    }
    ranked = semantic.search("atlas research engine", doc_vectors, top_k=2)
    assert ranked[0][0] == "relevant"


def test_ranking_engine_blends_scores():
    engine = RankingEngine(semantic_weight=0.5)
    candidates = [
        {"doc_id": "a", "bm25_score": 1.0, "semantic_score": 0.0},
        {"doc_id": "b", "bm25_score": 0.0, "semantic_score": 1.0},
    ]
    ranked = engine.rank(candidates)
    assert ranked[0]["final_score"] == ranked[1]["final_score"] == 0.5
