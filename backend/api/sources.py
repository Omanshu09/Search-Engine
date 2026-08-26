"""Endpoints for inspecting individual sources ATLAS has retrieved or indexed."""
from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import get_index_manager
from backend.indexing.index_manager import IndexManager
from backend.models.source_models import SourceDetail
from backend.utils.urls import get_domain

router = APIRouter()


@router.get("/{source_id}", response_model=SourceDetail)
def get_source(source_id: str, index_manager: IndexManager = Depends(get_index_manager)):
    """
    Return metadata and extracted content for a single source (used by the
    frontend's SourceList / citation drill-down). Only sources indexed
    during a search/research request in this process are available --
    there is no persistent cross-request store yet (see index_manager.load/persist TODOs).
    """
    doc = index_manager.get_document(source_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Source not found (not indexed in this session)")
    return SourceDetail(
        id=doc.doc_id,
        title=doc.title,
        url=doc.url,
        domain=get_domain(doc.url),
        content=doc.text,
    )
