"""
ATLAS backend entry point.

Boots the FastAPI application, wires up routers, and initializes shared
resources (index, document store, crawler manager, AI clients) via the
dependency container defined in dependencies.py.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.api import search, research, sources, health, feedback

settings = get_settings()

app = FastAPI(
    title="ATLAS",
    description="Web Research & Evidence Engine",
    version="0.1.0",
)

# TODO: restrict origins via settings.allowed_origins before deploying publicly
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])


@app.get("/")
def root():
    return {"name": "ATLAS", "status": "ok", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
