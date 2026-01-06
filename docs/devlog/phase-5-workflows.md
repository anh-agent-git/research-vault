# Phase 5: Workflows Implementation

## Overview

Implemented LangGraph-style workflows using simple async functions for paper ingestion, pattern review, and query synthesis.

**Status:** Complete
**Tests Added:** 50
**PRs:** TBD

---

## Architecture Decision: Simple Async Functions

**Approach:** Used simple async functions instead of LangGraph for MVP.

**Rationale:**
1. Our workflows are linear pipelines (no branching, no human-in-the-loop)
2. LangGraph adds complexity without benefit for linear flows
3. Existing services already handle retry/error logic
4. Can add LangGraph later if needed for complex orchestration

**Trade-offs:**
- Simpler implementation and testing
- Easier to debug (no graph state)
- LangSmith tracing still works via existing LLMClient
- No built-in checkpointing (not needed for MVP)
- Would need refactor for complex branching (future)

---

## Slice 1: Ingestion Workflow

**What:** Implemented `IngestionWorkflow` to process uploaded PDFs into papers and patterns.

**Flow:**
```
PDF bytes + metadata
    ↓
[1] Parse PDF (PDFParserService)
    ↓
[2] Extract metadata (MetadataExtractor)
    ↓
[3] Create Paper record (database)
    ↓
[4] Extract patterns (PatternExtractor)
    ↓
[5] Create Pattern records (database, status=pending)
    ↓
IngestionResult (paper_id, patterns, warnings)
```

**Files Created:**
- `backend/app/workflows/__init__.py`
- `backend/app/workflows/ingestion.py`
- `backend/tests/test_workflows/__init__.py`
- `backend/tests/test_workflows/test_ingestion.py`

**Types:**
```python
@dataclass
class IngestionInput:
    pdf_bytes: bytes
    user_metadata: PaperMetadataInput | None = None

@dataclass
class IngestionResult:
    paper_id: str
    pattern_count: int
    patterns: list[ExtractedPatternResponse]
    warnings: list[str]
    success: bool
    error: str | None = None
```

**Tests (18):**
- Happy path creates paper and patterns
- Returns paper ID (UUID format)
- Returns pattern responses for review
- PDF parse failure returns error
- Metadata extraction failure continues
- Pattern extraction failure continues (still creates paper)
- Empty patterns is valid
- Database commit failure returns error
- Propagates extraction warnings
- User metadata takes precedence
- Patterns have pending status
- Paper has ready_for_review status
- Unsuccessful extraction adds warning
- Input/Result dataclass tests

**Bug Fix:** Added `confidence` field to `ExtractedPatternResponse` schema (needed for review UI).

---

## Slice 2: Review Workflow

**What:** Implemented `ReviewWorkflow` to process pattern review decisions.

**Flow:**
```
PatternReviewRequest (list of decisions)
    ↓
[1] Validate pattern IDs exist
    ↓
[2] For approved patterns:
    ├── Generate embedding (EmbeddingService)
    ├── Upsert to vector store (VectorStoreService)
    └── Update status to 'approved' (database)
    ↓
[3] For rejected patterns:
    └── Update status to 'rejected' (database)
    ↓
[4] Update paper status if all patterns reviewed
    ↓
ReviewResult (approved_count, rejected_count, errors)
```

**Files Created:**
- `backend/app/workflows/review.py`
- `backend/tests/test_workflows/test_review.py`

**Types:**
```python
@dataclass
class ReviewResult:
    approved_count: int = 0
    rejected_count: int = 0
    errors: list[str] = field(default_factory=list)
    paper_status_updated: bool = False
    success: bool = True
```

**Tests (14):**
- Approve patterns generates embeddings
- Approve patterns upserts to vector store
- Approve updates pattern status
- Reject updates pattern status
- Reject does not embed
- Mixed decisions
- Embedding failure continues (pattern still approved)
- Vector store failure continues
- Invalid pattern ID adds error
- Paper not found returns error
- Database commit failure returns error
- Paper status updated when all reviewed
- Result dataclass tests

**Fix:** Used `PaperStatus.active` instead of non-existent `processed` status.

---

## Slice 3: Query Workflow

**What:** Implemented `QueryWorkflow` to search patterns and synthesize answers.

**Flow:**
```
Query + session_id
    ↓
[1] Get/create session (SessionManager)
    ↓
[2] Generate query embedding (EmbeddingService)
    ↓
[3] Search vector store (VectorStoreService)
    ↓
[4] Retrieve pattern details (database)
    ↓
[5] Build pattern context (synthesis.build_pattern_context)
    ↓
[6] Synthesize answer (LLMClient + synthesis prompt)
    ↓
[7] Update session with turn
    ↓
QueryResult (answer, sources, follow_ups, session_id)
```

**Files Created:**
- `backend/app/workflows/query.py`
- `backend/tests/test_workflows/test_query.py`

**Types:**
```python
@dataclass
class QueryInput:
    query: str
    session_id: str | None = None
    limit: int = 10

@dataclass
class QueryResult:
    answer: str = ""
    sources: list[SourceReference] = field(default_factory=list)
    confidence: str = "medium"
    follow_up_suggestions: list[str] = field(default_factory=list)
    session_id: str = ""
    success: bool = True
    error: str | None = None
```

**Tests (18):**
- New session creates session
- Existing session uses session
- Expired session creates new
- Generates query embedding
- Searches vector store
- Synthesizes answer
- Updates session with turns
- Returns sources
- Embedding failure returns error
- Vector search failure returns error
- Synthesis failure returns error
- No results returns helpful message
- Includes follow-up suggestions
- Includes confidence
- Input/Result dataclass tests

---

## Slice 4: Integration & Documentation

**What:** Updated exports and documentation.

**Files Modified:**
- `backend/app/workflows/__init__.py` - Added Review and Query exports
- `backend/CLAUDE.md` - Added Workflows section with usage examples
- `docs/devlog/phase-5-workflows.md` - This file
- `PLAN.md` - Updated status

---

## Key Implementation Patterns

### Dependency Injection for Testing

All workflows accept optional services for testing:

```python
class IngestionWorkflow:
    def __init__(
        self,
        db: AsyncSession,
        pdf_parser: PDFParserService | None = None,  # Inject for tests
        metadata_extractor: MetadataExtractor | None = None,
        pattern_extractor: PatternExtractor | None = None,
    ) -> None:
        self.db = db
        self._pdf_parser = pdf_parser
        # ...

    @property
    def pdf_parser(self) -> PDFParserService:
        """Lazy initialization of PDF parser."""
        if self._pdf_parser is None:
            self._pdf_parser = PDFParserService()
        return self._pdf_parser
```

### Partial Success Strategy

Workflows continue on non-critical failures:

```python
# Metadata extraction failure doesn't stop workflow
try:
    metadata = await self.metadata_extractor.extract(...)
except Exception as e:
    warnings.append(f"Metadata extraction failed: {e}")
    metadata = None  # Use defaults

# Pattern still approved even if embedding fails
try:
    embedding = await self.embedding_service.generate_embedding(text)
except Exception as e:
    result.errors.append(f"Embedding failed: {e}")
    embedding = None  # Skip vector store, but still approve
```

### Transaction Management

Database operations wrapped in transactions:

```python
async def run(self, input: IngestionInput) -> IngestionResult:
    # ... operations ...

    try:
        await self.db.commit()
    except Exception as e:
        await self.db.rollback()
        return IngestionResult(success=False, error=str(e))
```

---

## Test Summary

| Slice | Tests | Description |
|-------|-------|-------------|
| Slice 1 | 18 | Ingestion Workflow |
| Slice 2 | 14 | Review Workflow |
| Slice 3 | 18 | Query Workflow |
| **Total** | **50** | Phase 5 tests |

---

## Session Log

| Date | Engineer | What Changed |
|------|----------|--------------|
| 2026-01-05 | Claude | Phase 5 complete - all 3 workflows implemented |

---

## Open Questions / Next Steps

1. **API Routes (Phase 6):** Wire workflows to REST endpoints
2. **Error handling refinement:** May need more specific error types
3. **Observability:** Add structured logging/metrics
4. **Rate limiting:** Consider for LLM calls in query workflow
