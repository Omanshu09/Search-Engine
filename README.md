# ATLAS — Web Research & Evidence Engine

ATLAS is a web research and evidence engine, not a search-engine clone. Where a
conventional search engine hands back a list of links, ATLAS retrieves
information from multiple relevant sources, compares the evidence, identifies
agreement and contradiction between sources, and returns a structured,
source-backed answer.

The system distinguishes two modes:

- **Search** — discover relevant sources for a query and rank them.
- **Research** — investigate a question, synthesize evidence across sources,
  and return a cited answer.

This repository is the initial skeleton described in the project plan: real
working code where a fundamental (tokenizer, inverted index, BM25) is cheap to
get right early, and clearly marked `TODO`s where a component (crawling,
semantic search, LLM reasoning) is genuinely the next thing to build.

## Architecture

```
backend/
  main.py              FastAPI app entry point
  config.py            Environment-driven settings
  dependencies.py      Shared dependency providers (index, engines)
  api/                 HTTP endpoints (search, research, sources, health, feedback)
  core/                Orchestration: query processing, search/research engines,
                        evidence evaluation, ranking, citations
  crawler/             Web crawling: frontier, robots.txt, fetching, HTML parsing
  indexing/            Classic IR: tokenizer, inverted index, BM25, document store
  ai/                  Embeddings, semantic search, LLM client, RAG, claim extraction
  models/              Pydantic request/response/domain models
  utils/               Shared text/URL/logging helpers

frontend/
  src/
    pages/             Home (Search) and Research pages
    components/        SearchBar, SearchResults, ResultCard, ResearchAnswer, SourceList, Loading
    api.js             Fetch wrapper around the backend API

tests/                 pytest tests mirroring the backend layers
```

Request flow (target state): frontend → `query_processor` normalizes the
query → `search_engine` / `research_engine` decide what to retrieve →
`crawler` and/or `indexing` supply candidates → `bm25` (keyword) and
`semantic_search` (vector) score them → `ranking_engine` orders results →
for research, `evidence_engine` reconciles claims across sources,
`citation_engine` attaches sources, and `ai/rag.py` synthesizes the final
answer when an LLM is configured (otherwise an extractive fallback is used).

## Status

Every layer is implemented and wired end to end:

- **Indexing** — real tokenizer → inverted index → BM25.
- **Discovery** — `crawler.discover_seed_urls()` uses the free `ddgs` library
  to find candidate URLs for a query (the one place ATLAS leans on an
  external service, purely for URL discovery — not ranking or synthesis).
- **Crawling** — robots.txt-respecting, concurrent fetch + HTML extraction
  via httpx/BeautifulSoup.
- **Semantic search** — cosine similarity over embeddings; works out of the
  box with a dependency-free local hashing embedding, or against OpenAI's
  embeddings API if `EMBEDDING_MODEL_NAME=openai:...` is set.
- **Ranking** — blends normalized BM25 + semantic scores per
  `RANKING_SEMANTIC_WEIGHT`.
- **Evidence & citations** — claims are extracted per source (LLM-based if
  configured, heuristic sentence-selection otherwise), clustered across
  sources by similarity, and cited sources are de-duplicated in order.
- **Research synthesis** — `ai/rag.py` prompts an LLM (Anthropic or OpenAI,
  via direct REST calls, no SDK dependency) to answer with inline `[n]`
  citations; with no LLM configured it falls back to stitching together the
  highest-confidence claims extractively, so the app never hard-fails.

Nothing depends on a paid API key to run — without `LLM_PROVIDER`/
`LLM_API_KEY`/`EMBEDDING_MODEL_NAME` set, ATLAS still searches, crawls,
indexes, ranks, and produces an extractive research answer.

Search and research are query-scoped (each request crawls and indexes a
handful of freshly-discovered pages) rather than backed by a persistent,
pre-built whole-web index — see `index_manager.load()`/`persist()` for where
to add real persistence (SQLite/Postgres + a vector store) if you want
results to survive across requests/restarts.

## Local development

### Backend

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload
```

API docs will be available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://localhost:8000` (see
`frontend/vite.config.js`).

### Tests

```bash
pytest
```

### Docker Compose (optional, runs both together)

```bash
docker compose up --build
```

## Configuration

All configuration is environment-driven (see `.env.example`). Never commit a
real `.env` file — `config.py` reads settings via `pydantic-settings`, and
`.gitignore` already excludes `.env`.

ATLAS is designed to run in a reduced mode with no external services
configured: without `LLM_PROVIDER`/`LLM_API_KEY` set, research falls back to
extractive summarization instead of failing.

## Deployment notes

- The backend needs outbound internet access (for `ddgs` seed discovery,
  crawling target pages, and any configured LLM/embedding API), so it must
  run on a host that allows egress — a serverless/offline sandbox won't work.
- There is no persistence yet: the index and document store are in-memory
  per process. On a multi-worker/multi-instance deployment, each worker
  builds its own index per request; this is fine functionally but means no
  shared cache across workers. Add persistence (see `index_manager.py`) if
  you want that.
- Be a good citizen: `CRAWLER_USER_AGENT`, `CRAWLER_REQUEST_TIMEOUT_SECONDS`,
  and `MAX_CRAWL_CONCURRENCY` in `.env` control how ATLAS crawls; robots.txt
  is always respected.
- Set `ALLOWED_ORIGINS` in `.env` to your deployed frontend's real origin
  before going live — it currently only allows `localhost:5173`.

## Roadmap

Implemented: tokenizer → inverted index → BM25; seed discovery + crawling;
semantic search (local hashing embedding or OpenAI); blended ranking;
claim extraction; evidence clustering; citation de-duplication; LLM-backed
(or extractive-fallback) research synthesis; full API + React frontend.

Natural next steps, roughly in order of value:

1. Persistence for the index/document store (SQLite/Postgres) so results
   survive across requests instead of being rebuilt per query.
2. A real vector store (e.g. pgvector/FAISS) once persistence exists, to
   make semantic search scale past an in-memory dict.
3. Contradiction detection in `evidence_engine.py` (currently only clusters
   agreement; `contradicting_sources` is always empty).
4. Caching crawled pages/robots.txt across requests to reduce redundant
   fetches for popular queries.
5. Auth, rate limiting, and monitoring once this is exposed publicly at scale.

Further out: multilingual search, source-quality scoring, async task
workers, Redis/Kafka for larger-scale crawling — introduced only when
there's a concrete engineering reason, not to pad the stack.
