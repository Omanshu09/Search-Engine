"""
User feedback endpoints (e.g. thumbs up/down on a result or research
answer). Intended to eventually feed ranking-quality evaluation.
"""
from fastapi import APIRouter

from pydantic import BaseModel

router = APIRouter()


class FeedbackPayload(BaseModel):
    query: str
    result_id: str
    helpful: bool
    comment: str | None = None


@router.post("/")
def submit_feedback(payload: FeedbackPayload):
    """
    Record feedback for later analysis.

    TODO: persist to a feedback store (DB or log) instead of discarding it.
    """
    return {"status": "received"}
