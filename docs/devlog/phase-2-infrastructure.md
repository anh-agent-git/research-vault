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
| 2026-01-05 | Claude Opus 4.5 | Slice 3: Core services (PDF parser, LLM client) |
| 2026-01-05 | Claude Opus 4.5 | Slice 4: More services (VectorStoreService, SessionManager) |
| 2026-01-05 | Claude Opus 4.5 | Slice 5: Frontend scaffolding (Next.js 16.x, health check UI) |

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

## Slice 3: Core Services

### What We Did

- Created `backend/app/services/__init__.py`:
  - Exports PDFParserService, LLMClient, and related classes

- Created `backend/app/services/pdf_parser.py`:
  - PyMuPDF-based PDF text extraction
  - Page limit enforcement (default 50 pages)
  - Encrypted PDF detection
  - Metadata extraction (title, author, subject, creator)
  - Validation without full parsing

- Created `backend/app/services/llm_client.py`:
  - Async Claude API client with retry logic
  - Exponential backoff on rate limit and connection errors
  - Model ID validation (catches typos/deprecated models)
  - JSON response parsing with markdown handling
  - Configurable max_retries and timeout

- Created comprehensive tests:
  - `tests/test_services/test_pdf_parser.py` - 28 tests
  - `tests/test_services/test_llm_client.py` - 32 tests
  - Updated `tests/conftest.py` with LLM mock fixtures

### How We Verified

```bash
cd backend
uv run ruff check .                    # All checks passed
uv run pytest tests/ -v                # 82 tests passed
```

### Files Created

```
backend/
├── app/
│   └── services/
│       ├── __init__.py          # Service exports
│       ├── pdf_parser.py        # PDF text extraction
│       └── llm_client.py        # Claude API client
└── tests/
    ├── conftest.py              # Updated with LLM mocks
    └── test_services/
        ├── __init__.py
        ├── test_pdf_parser.py   # 28 tests
        └── test_llm_client.py   # 32 tests
```

### Test Coverage

| Service | Tests | Coverage |
|---------|-------|----------|
| PDFParserService | 28 | Init, parse, validate, errors, edge cases |
| LLMClient | 32 | Init, complete, retry, JSON parsing, model support |
| **Total New** | **60** | |

---

## Slice 4: More Services

### What We Did

- Created `backend/app/schemas/__init__.py`:
  - Exports ConversationSession, ConversationTurn, SourceReference

- Created `backend/app/schemas/session.py`:
  - SourceReference schema with pattern_id, summary, relevance_score
  - ConversationTurn schema (role, content, sources, timestamp)
  - ConversationSession schema (session_id, history, timestamps)

- Created `backend/app/services/vector_store.py`:
  - Qdrant client wrapper for pattern embeddings
  - `ensure_collection()` - Creates collection if not exists
  - `health_check()` - Verifies Qdrant connectivity
  - `upsert_pattern()` - Store/update pattern embeddings
  - `delete_pattern()` - Remove pattern from vector store
  - `search()` - Semantic search with filters and limits
  - `get_collection_info()` - Collection statistics

- Created `backend/app/services/session_manager.py`:
  - Thread-safe in-memory session storage with TTL
  - `create_session()` - Create new session with UUID
  - `get_session()` - Retrieve session (returns None if expired)
  - `update_session()` - Add conversation turn to session
  - `delete_session()` - Remove session by ID
  - `cleanup_expired()` - Remove all expired sessions
  - Background cleanup task with configurable interval
  - Content truncation for oversized responses (B-006)
  - History length limit with sliding window (100 turns)
  - Maximum sessions limit (10,000) to prevent memory exhaustion

- Updated `backend/app/services/__init__.py`:
  - Exports VectorStoreService, SessionManager, session_manager

- Updated `backend/app/main.py`:
  - Added SessionManager cleanup task to lifespan
  - Health check now uses VectorStoreService for real Qdrant status
  - Health check returns actual session count from SessionManager
  - Status logic: "ok" (both healthy), "degraded" (db only), "error"

- Updated `backend/tests/test_api/test_health.py`:
  - Updated tests to reflect new status logic
  - Qdrant status now "ok" or "error" (not "not_configured")

- Created comprehensive tests:
  - `tests/test_services/test_vector_store.py` - 33 tests
  - `tests/test_services/test_session_manager.py` - 45 tests

### How We Verified

```bash
cd backend
uv run ruff check .                    # All checks passed
uv run pytest tests/ -v                # 160 tests passed
```

### Files Created

```
backend/
├── app/
│   ├── schemas/
│   │   ├── __init__.py          # Schema exports
│   │   └── session.py           # Session schemas
│   └── services/
│       ├── __init__.py          # Updated exports
│       ├── vector_store.py      # Qdrant client wrapper
│       └── session_manager.py   # Session storage with TTL
└── tests/
    └── test_services/
        ├── test_vector_store.py     # 33 tests
        └── test_session_manager.py  # 45 tests
```

### Test Coverage

| Service | Tests | Coverage |
|---------|-------|----------|
| VectorStoreService | 33 | Init, ensure_collection, health_check, upsert, delete, search, get_info |
| SessionManager | 45 | Init, create, get, update, delete, cleanup, TTL, limits, async tasks, schemas |
| **Total New** | **78** | |

---

## Decisions Made (Slice 4)

| Decision | Rationale |
|----------|-----------|
| Minimal SourceReference schema | Full implementation with paper details comes in query phase |
| Global session_manager singleton | Matches source repo pattern, used in lifespan |
| Thread lock for session storage | Ensures thread-safety with async cleanup |
| Content truncation at 100KB | Prevents memory exhaustion from large responses |
| 100 turn history limit | Sliding window prevents unbounded memory growth |
| 10,000 max sessions | Protects against memory exhaustion |

---

## Slice 5: Frontend Scaffolding

### What We Did

- Created `frontend/package.json`:
  - Next.js 16.1.1 with React 19.2.3
  - Tailwind CSS v4 with tw-animate-css
  - Lucide React for icons
  - next-themes for dark mode support
  - ESLint 9 with Prettier

- Created configuration files:
  - `tsconfig.json` - TypeScript with path aliases (@/*)
  - `next.config.ts` - Standalone output for Docker
  - `postcss.config.mjs` - Tailwind CSS PostCSS plugin
  - `eslint.config.mjs` - Flat ESLint config with Next.js + Prettier
  - `.prettierrc` - Consistent formatting

- Created `frontend/src/app/`:
  - `layout.tsx` - Root layout with ThemeProvider and header
  - `page.tsx` - Home page with health check dashboard
  - `globals.css` - Tailwind imports and CSS custom properties

- Created `frontend/src/components/`:
  - `theme-provider.tsx` - next-themes wrapper

- Created `frontend/src/lib/`:
  - `api.ts` - API client with health check endpoint
  - `utils.ts` - cn() utility for className merging

### How We Verified

```bash
cd frontend
npm install                           # Installed 364 packages
npm run build                         # Build succeeded
npm run lint                          # No errors
```

### Files Created

```
frontend/
├── package.json                # Dependencies + scripts
├── tsconfig.json               # TypeScript config
├── next.config.ts              # Next.js config
├── postcss.config.mjs          # PostCSS config
├── eslint.config.mjs           # ESLint flat config
├── .prettierrc                 # Prettier config
├── .gitignore                  # Git ignores
├── .env.example                # Example environment
├── public/                     # Static assets (empty)
└── src/
    ├── app/
    │   ├── globals.css         # Tailwind + theme CSS
    │   ├── layout.tsx          # Root layout
    │   └── page.tsx            # Home with health check
    ├── components/
    │   └── theme-provider.tsx  # Theme wrapper
    └── lib/
        ├── api.ts              # Backend API client
        └── utils.ts            # Utility functions
```

### Features

- **Health Check Dashboard**: Real-time status of database, Qdrant, sessions, tracing
- **Dark Mode Support**: System preference detection with manual toggle ready
- **Responsive Design**: Mobile-friendly layout with Tailwind CSS
- **Auto-Refresh**: Health status updates every 30 seconds
- **Error Handling**: User-friendly error display when backend unavailable

---

## Open Questions / Next Steps

**Next Slice (Slice 6):** Docker setup
- docker-compose.yml with backend, frontend, Qdrant
- Dockerfiles for backend and frontend
- Integration testing with real services

**Phase 2 Completion:**
- After Slice 6, Phase 2 (Infrastructure) will be complete
- Phase 3 will add database models and API routes
