"""
Research endpoints.

Research is about *investigating a question*: retrieving evidence from
multiple sources, comparing and reconciling it, and returning a structured,
citation-backed answer (as opposed to a plain list of links).
"""
from fastapi import APIRouter, Depends

from backend.dependencies import get_research_engine
from backend.core.research_engine import ResearchEngine
from backend.models.research_models import ResearchRequest, ResearchResponse

router = APIRouter()


@router.post("/", response_model=ResearchResponse)
def research(request: ResearchRequest, engine: ResearchEngine = Depends(get_research_engine)):
    """
    Run a full research pipeline: retrieve evidence, rank it, extract
    claims, resolve agreements/contradictions, and synthesize a cited
    answer.

    TODO: implement once evidence_engine, citation_engine, and the AI
    reasoning layer (ai/rag.py) are in place.
    """
    return engine.research(request)
