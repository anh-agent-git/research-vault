# Phase 2: Infrastructure Migration

## Goal

Migrate core infrastructure from source repo (no business logic yet).

## Outcome

Backend and frontend scaffolding with database and vector store setup.

---

## Session Log

| Date | Engineer | What Changed |
|------|----------|--------------|
| 2025-01-05 | Claude Opus 4.5 | Slice 1: Backend scaffolding (pyproject.toml, main.py, config.py) |

---

## Slice 1: Backend Scaffolding

### What We Did

- Created `backend/pyproject.toml` with dependencies:
  - FastAPI, SQLAlchemy, Alembic, Pydantic
  - Anthropic, OpenAI clients
  - LangGraph, Qdrant client
  - PyMuPDF for PDF parsing
  - Dev dependencies: pytest, ruff, httpx

- Created `backend/app/__init__.py` (module marker)

- Created `backend/app/main.py`:
  - FastAPI app with lifespan handler
  - CORS middleware for frontend
  - Health check endpoint (`/health`)
  - OpenAPI tags (papers, patterns, query)
  - LangSmith tracing configuration
  - Removed all SRAL references from descriptions

- Created `backend/app/config.py`:
  - Pydantic Settings for environment variables
  - ModelID class for Anthropic model validation
  - Settings: API keys, database, Qdrant, ingestion, LangSmith

### How We Verified

```bash
cd backend
uv sync                          # Installed 71 packages
uv run python -c "from app.main import app; print(app.title)"
# Output: Research Vault API
```

### Files Created

```
backend/
├── pyproject.toml          # Dependencies + tool config
└── app/
    ├── __init__.py         # Module marker
    ├── main.py             # FastAPI entry point
    └── config.py           # Pydantic Settings
```

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Minimal main.py for Slice 1 | Full features (db, vector store) added in later slices |
| Health check returns "not_configured" for db/qdrant | Services not yet implemented |
| Kept LangSmith tracing support | Useful for debugging workflows |

---

## Open Questions / Next Steps

**Next Slice (Slice 2):** Database setup
- `app/db/session.py` - Async SQLAlchemy session
- `alembic/` - Migration structure
- Update health check to use real db connection

**Remaining Slices:**
- Slice 3: Core services (PDF parser, LLM client)
- Slice 4: More services (Vector store, Session manager)
- Slice 5: Frontend scaffolding
- Slice 6: Docker setup
