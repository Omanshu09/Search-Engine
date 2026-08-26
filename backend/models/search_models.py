"""Pydantic request/response models for the /api/search endpoints."""
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Raw user search query")
    top_k: int = Field(10, ge=1, le=50)
    use_semantic_search: bool = True


class SearchResultItem(BaseModel):
    id: str
    title: str
    url: str
    snippet: str
    score: float
    source_domain: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem] = []
    total_results: int = 0
    took_ms: Optional[float] = None
