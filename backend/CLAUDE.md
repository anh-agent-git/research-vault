# Backend Context

## Overview

FastAPI backend for Research Vault. Handles paper ingestion, pattern extraction, and query synthesis.

## Tech Stack

- **Framework:** FastAPI 0.128.x
- **Database:** SQLite with aiosqlite (async), SQLAlchemy 2.x
- **Migrations:** Alembic (async)
- **Vector Store:** Qdrant 1.16.x
- **LLM:** Anthropic Claude API
- **Embeddings:** OpenAI text-embedding-3-small
- **PDF Parsing:** PyMuPDF 1.26.x
- **Package Manager:** uv

## Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, lifespan, CORS
│   ├── config.py            # Pydantic Settings
│   ├── db/
│   │   ├── __init__.py      # Exports session, engine, get_db
│   │   └── session.py       # Async SQLAlchemy setup
│   ├── models/
│   │   ├── __init__.py      # Exports Base, Paper, Pattern, enums
│   │   ├── base.py          # DeclarativeBase
│   │   ├── paper.py         # Paper model + PaperType, PaperStatus enums
│   │   └── pattern.py       # Pattern model + PatternStatus enum
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── session.py       # ConversationSession, Turn, SourceReference
│   │   ├── paper.py         # PaperMetadataInput, PaperMetadataExtracted, PaperResponse
│   │   └── query.py         # QueryRequest, QueryResponse, FollowUpRequest
│   ├── services/
│   │   ├── __init__.py           # Service exports
│   │   ├── pdf_parser.py         # PDFParserService
│   │   ├── llm_client.py         # LLMClient with retry
│   │   ├── vector_store.py       # VectorStoreService (Qdrant)
│   │   ├── session_manager.py    # SessionManager with TTL
│   │   ├── metadata_extractor.py # MetadataExtractor (paper metadata)
│   │   ├── pattern_extractor.py  # PatternExtractor (3-pass pipeline)
│   │   ├── embedding_service.py  # EmbeddingService (OpenAI embeddings)
│   │   └── prompts/
│   │       ├── __init__.py           # Prompt exports
│   │       ├── metadata.py           # Metadata extraction prompts
│   │       ├── evidence_inventory.py # Pass 1: Evidence inventory
│   │       ├── extraction.py         # Pass 2: Pattern extraction
│   │       ├── verification.py       # Pass 3: Verification
│   │       └── synthesis.py          # Query synthesis prompts
│   └── workflows/
│       ├── __init__.py       # Workflow exports
│       ├── ingestion.py      # PDF → Paper + Patterns
│       ├── review.py         # Pattern decisions → Embeddings + Vector store
│       └── query.py          # Query → Search → Synthesize
│   └── routers/
│       ├── __init__.py       # Router exports
│       ├── papers.py         # Paper CRUD routes
│       ├── patterns.py       # Pattern management routes
│       └── query.py          # Query routes
├── alembic/
│   ├── env.py               # Async migration environment
│   └── versions/            # Migration files
├── tests/
│   ├── conftest.py          # Fixtures (db, mocks)
│   ├── test_api/
│   │   ├── test_health.py
│   │   ├── test_papers.py    # Paper route tests
│   │   ├── test_patterns.py  # Pattern route tests
│   │   └── test_query.py     # Query route tests
│   ├── test_services/
│   │   ├── test_pdf_parser.py
│   │   ├── test_llm_client.py
│   │   ├── test_vector_store.py
│   │   └── test_session_manager.py
│   └── test_workflows/
│       ├── test_ingestion.py    # Ingestion workflow tests
│       ├── test_review.py       # Review workflow tests
│       └── test_query.py        # Query workflow tests
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── Dockerfile
└── .dockerignore
```

## Key Patterns

### Async Database

```python
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/example")
async def example(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Model))
    return result.scalars().all()
```

### Service Pattern

Services are stateless classes instantiated with configuration:

```python
from app.services import PDFParserService, LLMClient, VectorStoreService

# PDF parsing
parser = PDFParserService(max_pages=50)
result = parser.parse(pdf_bytes)

# LLM calls (async)
client = LLMClient(api_key="...", model_id="claude-sonnet-4-20250514")
response = await client.complete(system_prompt, user_message)

# Vector store (async)
vector_store = VectorStoreService(host="localhost", port=6333)
await vector_store.ensure_collection()
results = await vector_store.search(embedding, limit=10)
```

### Session Manager

Global singleton for conversation state:

```python
from app.services import session_manager

session = session_manager.create_session()
session_manager.update_session(session_id, turn)
session = session_manager.get_session(session_id)  # None if expired
```

### Pattern Extraction (3-Pass Pipeline)

Evidence-anchored extraction using multi-model strategy:

```python
from app.services import PatternExtractor

# Create extractor (uses Haiku for Pass 1/3, Sonnet for Pass 2)
extractor = PatternExtractor()

# Extract patterns from paper text
result = await extractor.extract(
    text="Paper content...",
    metadata_context="Title: Example Paper"  # optional
)

# Result contains:
# - result.patterns: ExtractionResult with extracted patterns
# - result.evidence_inventory: EvidenceInventory from Pass 1
# - result.verification: VerificationResult from Pass 3
# - result.warnings: List of user-facing warnings
# - result.is_successful: True if verification passed/warned
# - result.pattern_count: Number of extracted patterns
```

### Embedding Service

Generate embeddings for patterns:

```python
from app.services import EmbeddingService

service = EmbeddingService()  # Uses OPENAI_API_KEY from settings

# Prepare text from pattern data
text = service.prepare_embedding_text({
    "name": "Pattern Name",
    "claim": "Main claim",
    "evidence": "Supporting evidence",
    "context": "Additional context",
})  # Returns: "Pattern Name | Main claim | Supporting evidence | ..."

# Generate single embedding
result = await service.generate_embedding(text)
embedding = result.embedding  # list[float], 1536 dimensions

# Batch generate embeddings
results = await service.generate_embeddings_batch(patterns)
for pattern, embedding in results:
    # Store pattern with its embedding
    pass
```

### Metadata Extraction

Extract paper metadata using LLM:

```python
from app.services import MetadataExtractor

extractor = MetadataExtractor()

# Extract from paper text with optional hints
metadata = await extractor.extract(
    text="Paper content...",
    pdf_hints={"title": "From PDF metadata"},  # optional
    user_overrides={"paper_type": "empirical"},  # optional, takes precedence
)

# metadata contains: title, authors, year, paper_type, one_sentence_summary
```

### Health Check Response

```json
{
  "status": "ok|degraded|error",
  "database": "ok|error",
  "qdrant": "ok|error",
  "sessions": 0,
  "tracing": "enabled|disabled"
}
```

### Workflows

Workflows orchestrate services into end-to-end pipelines. All workflows use async patterns and support dependency injection for testing.

#### Ingestion Workflow

Processes uploaded PDFs into papers and patterns:

```python
from app.workflows import IngestionWorkflow, IngestionInput

workflow = IngestionWorkflow(db=session)
result = await workflow.run(IngestionInput(
    pdf_bytes=pdf_content,
    user_metadata=PaperMetadataInput(title="Custom Title"),  # optional
))

# result.success: bool
# result.paper_id: str (UUID)
# result.pattern_count: int
# result.patterns: list[ExtractedPatternResponse]
# result.warnings: list[str]
```

Flow: Parse PDF → Extract metadata → Create Paper → Extract patterns → Create Patterns (pending)

#### Review Workflow

Processes pattern review decisions:

```python
from app.workflows import ReviewWorkflow
from app.schemas.pattern import PatternDecision

workflow = ReviewWorkflow(db=session)
result = await workflow.run(
    paper_id="paper-uuid",
    decisions=[
        PatternDecision(temp_id="pattern-1", approved=True),
        PatternDecision(temp_id="pattern-2", approved=False),
    ],
)

# result.approved_count: int
# result.rejected_count: int
# result.paper_status_updated: bool (True if all patterns reviewed)
# result.errors: list[str]
```

Flow: Validate patterns → Embed approved → Upsert to vector store → Update status

#### Query Workflow

Searches patterns and synthesizes answers:

```python
from app.workflows import QueryWorkflow, QueryInput

workflow = QueryWorkflow(db=session)
result = await workflow.run(QueryInput(
    query="What patterns exist about agent memory?",
    session_id=None,  # None creates new session
    limit=10,
))

# result.answer: str (with [P:id] citations)
# result.sources: list[SourceReference]
# result.confidence: str (high/medium/low)
# result.follow_up_suggestions: list[str]
# result.session_id: str (for follow-up queries)
```

Flow: Get/create session → Embed query → Search vectors → Retrieve patterns → Synthesize → Update session

### API Routes

Routes are thin wrappers that validate input, call workflows, and format output.

#### Paper Routes (`/api/papers`)

```python
from app.routers import papers_router

# POST /api/papers - Upload paper (PDF or text)
# Accepts multipart form: file (PDF) OR text, plus optional metadata fields
# Returns: paper_id, metadata, patterns (pending), warnings

# GET /api/papers - List papers with filters
# Query params: status, type, limit, offset
# Returns: papers list with pattern_count, total count

# GET /api/papers/{paper_id} - Get single paper
# Returns: full paper details with pattern_count

# DELETE /api/papers/{paper_id} - Delete paper and all patterns
# Also removes patterns from vector store
```

#### Pattern Routes (`/api/papers/{id}/patterns`, `/api/patterns`)

```python
from app.routers import paper_patterns_router, patterns_router

# POST /api/papers/{paper_id}/patterns - Submit review decisions
# Body: {"decisions": [{"temp_id": "...", "approved": true/false}]}
# Returns: approved_count, rejected_count, patterns

# GET /api/papers/{paper_id}/patterns - List patterns for paper
# Query params: status
# Returns: patterns list

# PUT /api/patterns/{pattern_id} - Update pattern
# Body: partial pattern fields (name, claim, evidence, context, tags)
# Triggers re-embedding if content fields change

# DELETE /api/patterns/{pattern_id} - Delete pattern
# Also removes from vector store
```

#### Query Routes (`/api/query`)

```python
from app.routers import query_router

# POST /api/query - Submit query (creates or uses session)
# Body: {"query": "...", "session_id": "..." (optional)}
# Returns: session_id, response, sources, confidence, follow_up_suggestions

# POST /api/query/followup - Follow-up query (requires session)
# Body: {"query": "...", "session_id": "..." (required)}
# Returns: same as above, uses conversation history
```

#### Route Pattern

All routes follow this pattern:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db

router = APIRouter(prefix="/api/resource", tags=["resource"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_resource(
    request: RequestSchema,
    db: AsyncSession = Depends(get_db),
) -> ResponseSchema:
    workflow = SomeWorkflow(db=db)
    result = await workflow.run(...)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ERROR_CODE", "message": result.error},
        )

    return ResponseSchema(...)
```

## Common Commands

```bash
# Install dependencies
uv sync

# Run server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest tests/ -v

# Lint & format
uv run ruff check .
uv run ruff format .

# Run migrations
uv run alembic upgrade head

# Create migration
uv run alembic revision --autogenerate -m "description"
```

## Test Conventions

- Use `pytest-asyncio` for async tests
- Mock external services (LLM, Qdrant) in unit tests
- Test fixtures in `conftest.py`
- Naming: `test_<function>_<scenario>`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| ANTHROPIC_API_KEY | Yes | - | Claude API key |
| OPENAI_API_KEY | Yes | - | Embeddings API key |
| DATABASE_URL | No | sqlite:///./data/research.db | SQLite path |
| QDRANT_HOST | No | localhost | Qdrant server |
| QDRANT_PORT | No | 6333 | Qdrant port |
| LANGCHAIN_TRACING_V2 | No | false | Enable LangSmith |
| LANGCHAIN_API_KEY | No | - | LangSmith API key |
