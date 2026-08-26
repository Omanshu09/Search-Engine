"""Shared models describing a retrieved web source."""
from typing import Optional
from pydantic import BaseModel


class SourceRef(BaseModel):
    id: str
    title: str
    url: str
    domain: Optional[str] = None


class SourceDetail(SourceRef):
    fetched_at: Optional[str] = None
    content: Optional[str] = None
    reliability_score: Optional[float] = None
