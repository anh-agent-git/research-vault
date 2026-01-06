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
| 2026-01-05 | Claude Opus 4.5 | Slice 2: Database setup (async SQLAlchemy, Alembic, health check) |

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

## Slice 2: Database Setup

### What We Did

- Created `backend/app/db/__init__.py`:
  - Exports async_session_maker, engine, get_db

- Created `backend/app/db/session.py`:
  - Async SQLAlchemy engine with aiosqlite
  - Auto-converts sqlite:/// to sqlite+aiosqlite:///
  - Session factory with expire_on_commit=False
  - get_db dependency for FastAPI routes

- Created `backend/app/models/base.py`:
  - SQLAlchemy DeclarativeBase for all models
  - Placeholder for Phase 3 models

- Set up Alembic migration structure:
  - `alembic.ini` - Configuration
  - `alembic/env.py` - Async migration environment
  - `alembic/script.py.mako` - Migration template
  - `alembic/versions/` - Empty (models in Phase 3)

- Updated `backend/app/main.py`:
  - Added real database health check
  - Status logic: "degraded" when DB OK but Qdrant not configured

- Created tests:
  - `tests/conftest.py` - Database fixtures
  - `tests/test_api/test_health.py` - 6 health endpoint tests

### How We Verified

```bash
cd backend
uv run ruff check .                    # All checks passed
uv run pytest tests/ -v                # 6 tests passed
uv run alembic current                 # Alembic works
curl http://127.0.0.1:8765/health
# {"status":"degraded","database":"ok","qdrant":"not_configured","sessions":0,"tracing":"disabled"}
```

### Files Created

```
backend/
├── alembic.ini
├── alembic/
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions/        # Empty (models in Phase 3)
├── app/
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py
│   └── models/
│       ├── __init__.py
│       └── base.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_api/
        ├── __init__.py
        └── test_health.py
```

---

## Open Questions / Next Steps

**Next Slice (Slice 3):** Core services
- `app/services/pdf_parser.py` - PyMuPDF text extraction
- `app/services/llm_client.py` - Async Claude client

**Remaining Slices:**
- Slice 4: More services (Vector store, Session manager)
- Slice 5: Frontend scaffolding
- Slice 6: Docker setup
