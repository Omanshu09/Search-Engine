"""
Centralized configuration for ATLAS.

Loads environment variables (via .env in development) into a typed Settings
object. Nothing in this file should hold secrets directly -- all sensitive
values must come from the environment.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ATLAS"
    environment: str = "development"
    debug: bool = True

    # API
    allowed_origins: List[str] = ["http://localhost:5173"]

    # Crawling
    crawler_user_agent: str = "ATLASBot/0.1 (+https://example.com/atlas-bot)"
    crawler_max_concurrent_requests: int = 5
    crawler_request_timeout_seconds: int = 10
    crawler_respect_robots_txt: bool = True

    # Indexing
    index_storage_path: str = "./data/index"

    # AI / external services (optional, empty by default -- ATLAS degrades
    # gracefully to non-LLM behavior when these are unset)
    llm_provider: str = ""  # "anthropic" | "openai" | ""
    llm_api_key: str = ""
    llm_model: str = ""
    embedding_model_name: str = ""  # e.g. "openai:text-embedding-3-small"; blank = local fallback

    # Search backend
    search_api_key: str = ""

    # Live search / research pipeline
    seed_urls_per_query: int = 8
    max_crawl_concurrency: int = 5
    ranking_semantic_weight: float = 0.4  # BM25 weight is (1 - this)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
