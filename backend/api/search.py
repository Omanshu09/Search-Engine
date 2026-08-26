"""
Search endpoints.

Search is about *discovering relevant sources* for a query -- it returns a
ranked list of results, not a synthesized answer. See research.py for
question-answering / evidence synthesis.
"""
from fastapi import APIRouter, Depends

from backend.dependencies import get_search_engine
from backend.core.search_engine import SearchEngine
from backend.models.search_models import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/", response_model=SearchResponse)
def search(request: SearchRequest, engine: SearchEngine = Depends(get_search_engine)):
    """
    Run a search query and return ranked results.

    TODO: wire through to SearchEngine.search() once query processing,
    indexing, and ranking are implemented.
    """
    return engine.search(request)
