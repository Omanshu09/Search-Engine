"""
Text embedding generation for semantic search.

Two backends:
- If `model_name` is set as "openai:<model>", calls the OpenAI embeddings
  API (requires OPENAI-compatible key in config.llm_api_key or a dedicated
  key -- see EmbeddingClient.__init__).
- Otherwise, falls back to a dependency-free deterministic hashing
  embedding (a bag-of-words vector hashed into a fixed dimension and
  L2-normalized). This is not "real" semantic understanding, but it gives
  ATLAS a working, zero-cost semantic-similarity signal out of the box so
  the pipeline is never blocked on external services being configured.
"""
import hashlib
import math
from typing import List

import httpx

from backend.indexing.tokenizer import Tokenizer

_HASH_DIM = 256


class EmbeddingClient:
    def __init__(self, model_name: str = "", api_key: str = ""):
        self.model_name = model_name
        self.api_key = api_key
        self._tokenizer = Tokenizer(remove_stopwords=True)

    def embed(self, text: str) -> List[float]:
        if self.model_name.startswith("openai:"):
            return self._embed_openai(text)
        return self._embed_hashing(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]

    def _embed_hashing(self, text: str) -> List[float]:
        vector = [0.0] * _HASH_DIM
        tokens = self._tokenizer.tokenize(text)
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            index = int(digest, 16) % _HASH_DIM
            vector[index] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def _embed_openai(self, text: str) -> List[float]:
        model = self.model_name.split("openai:", 1)[1]
        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": model, "input": text},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
