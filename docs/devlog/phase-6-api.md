# Phase 6: API Routes

## Overview

**Goal:** Implement REST API endpoints that wire existing workflows to HTTP routes.

**Outcome:** Full API for papers, patterns, and queries per API_SPEC.md.

**Dependencies:** Phase 5 (workflows exist and tested)

---

## Slice 1: Paper Routes

### What We Did

Implemented paper CRUD endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| POST | /api/papers | Upload paper (PDF or text) |
| GET | /api/papers | List papers with filters |
| GET | /api/papers/{id} | Get single paper |
| DELETE | /api/papers/{id} | Delete paper and patterns |

### Key Implementation Details

1. **Multipart form uploads**: Used `File()` and `Form()` for PDF/text uploads with metadata
2. **Extended IngestionInput**: Added `text` field to support plain text uploads (not just PDFs)
3. **VectorStoreService.delete_by_paper_id()**: New method for bulk deletion when deleting papers
4. **Pagination**: List endpoint returns `papers`, `total`, `limit`, `offset`
5. **Pattern count**: Added to paper responses via separate query

### Files Created

- `backend/app/routers/__init__.py` - Router exports
- `backend/app/routers/papers.py` - Paper routes
- `backend/tests/test_api/test_papers.py` - 20 tests

### Files Modified

- `backend/app/workflows/ingestion.py` - Extended IngestionInput for text support
- `backend/app/services/vector_store.py` - Added delete_by_paper_id(), default params
- `backend/pyproject.toml` - Added B008 ignore for router files

---

## Slice 2: Pattern Routes

### What We Did

Implemented pattern management endpoints with two routers:

| Method | Path | Purpose |
|--------|------|---------|
| POST | /api/papers/{id}/patterns | Submit review decisions |
| GET | /api/papers/{id}/patterns | List patterns for paper |
| PUT | /api/patterns/{id} | Update pattern |
| DELETE | /api/patterns/{id} | Delete pattern |

### Key Implementation Details

1. **Two routers**: `paper_patterns_router` (scoped to paper) and `patterns_router` (direct access)
2. **Re-embedding on update**: When content fields change, regenerate embedding and upsert to vector store
3. **Query param aliases**: Used `Query(None, alias="status")` to match API spec naming
4. **VectorStoreService.upsert()**: Added async alias for workflow compatibility

### Files Created

- `backend/app/routers/patterns.py` - Pattern routes
- `backend/tests/test_api/test_patterns.py` - 15 tests

### Files Modified

- `backend/app/routers/__init__.py` - Added pattern router exports
- `backend/app/services/vector_store.py` - Added async upsert() alias
- `backend/app/main.py` - Included pattern routers

---

## Slice 3: Query Routes

### What We Did

Implemented query endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| POST | /api/query | Submit query (creates/uses session) |
| POST | /api/query/followup | Follow-up query (requires session) |

### Key Implementation Details

1. **Session management**: Creates new session if none provided, reuses existing
2. **Error differentiation**: Follow-up with expired session returns 404, other failures return 500
3. **Structured responses**: QueryResponse with session_id, response, sources, confidence, suggestions

### Files Created

- `backend/app/schemas/query.py` - Request/response schemas
- `backend/app/routers/query.py` - Query routes
- `backend/tests/test_api/test_query.py` - 9 tests

### Files Modified

- `backend/app/routers/__init__.py` - Added query router export
- `backend/app/main.py` - Included query router

---

## Slice 4: Integration & Documentation

### What We Did

1. Updated `backend/CLAUDE.md` with API routes documentation
2. Created this devlog
3. Updated `PLAN.md` with Phase 6 completion

---

## Technical Decisions

### B008 Lint Ignore for Routers

FastAPI's standard pattern uses function calls in default arguments:
```python
async def endpoint(db: AsyncSession = Depends(get_db)):
```

This triggers ruff B008 (function call in default argument). Added per-file ignore in `pyproject.toml`:
```toml
[tool.ruff.lint.per-file-ignores]
"app/routers/*.py" = ["B008"]
```

### Query Parameter Aliases

API spec uses `status` and `type` as query params, but these conflict with Python builtins. Used FastAPI's alias feature:
```python
status_filter: str | None = Query(None, alias="status")
type_filter: str | None = Query(None, alias="type")
```

### VectorStoreService Default Parameters

Made constructor parameters optional with defaults from settings:
```python
def __init__(
    self,
    host: str | None = None,
    port: int | None = None,
):
    self._host = host or settings.qdrant_host
    self._port = port or settings.qdrant_port
```

This simplifies route code that just needs default configuration.

---

## Test Summary

| Slice | Tests | Description |
|-------|-------|-------------|
| Slice 1 | 20 | Paper routes (upload, list, get, delete) |
| Slice 2 | 15 | Pattern routes (review, list, update, delete) |
| Slice 3 | 9 | Query routes (query, follow-up) |
| **Total** | **44** | Phase 6 tests |

All tests use mocked workflows to avoid external dependencies.

---

## Session Log

| Date | Engineer | What Changed |
|------|----------|--------------|
| 2026-01-05 | Claude | Implemented Slices 1-4: Full API routes with 44 tests |

---

## API Summary

### Endpoints Added

| Method | Path | Purpose |
|--------|------|---------|
| POST | /api/papers | Upload paper (PDF or text) |
| GET | /api/papers | List papers with filters |
| GET | /api/papers/{id} | Get single paper |
| DELETE | /api/papers/{id} | Delete paper and patterns |
| POST | /api/papers/{id}/patterns | Submit review decisions |
| GET | /api/papers/{id}/patterns | List patterns for paper |
| PUT | /api/patterns/{id} | Update pattern |
| DELETE | /api/patterns/{id} | Delete pattern |
| POST | /api/query | Submit query |
| POST | /api/query/followup | Follow-up query |

### Error Response Format

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable description"
}
```

Common codes: `VALIDATION_ERROR`, `NOT_FOUND`, `EXTRACTION_FAILED`, `QUERY_FAILED`, `SESSION_NOT_FOUND`
