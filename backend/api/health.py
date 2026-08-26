"""Health/readiness endpoints used by uptime checks and load balancers."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health_check():
    """Basic liveness probe."""
    return {"status": "ok"}


@router.get("/ready")
def readiness_check():
    """
    Readiness probe.

    TODO: verify the index, document store, and any required external
    services (LLM provider, embedding service) are reachable before
    reporting ready.
    """
    return {"status": "ready"}
