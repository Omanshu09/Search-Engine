"""Pydantic request/response models for the /api/research endpoints."""
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.models.source_models import SourceRef


class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=1)
    max_sources: int = Field(8, ge=1, le=25)
    depth: str = Field("standard", description="'quick' | 'standard' | 'deep'")


class ClaimEvidence(BaseModel):
    claim: str
    supporting_sources: List[SourceRef] = []
    contradicting_sources: List[SourceRef] = []
    confidence: Optional[float] = None


class ResearchResponse(BaseModel):
    question: str
    answer: str
    claims: List[ClaimEvidence] = []
    sources: List[SourceRef] = []
    took_ms: Optional[float] = None
