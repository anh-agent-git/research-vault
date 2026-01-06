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
│   │   └── paper.py         # PaperMetadataInput, PaperMetadataExtracted, PaperResponse
│   └── services/
│       ├── __init__.py      # Service exports
│       ├── pdf_parser.py    # PDFParserService
│       ├── llm_client.py    # LLMClient with retry
│       ├── vector_store.py  # VectorStoreService (Qdrant)
│       └── session_manager.py # SessionManager with TTL
├── alembic/
│   ├── env.py               # Async migration environment
│   └── versions/            # Migration files
├── tests/
│   ├── conftest.py          # Fixtures (db, mocks)
│   ├── test_api/
│   │   └── test_health.py
│   └── test_services/
│       ├── test_pdf_parser.py
│       ├── test_llm_client.py
│       ├── test_vector_store.py
│       └── test_session_manager.py
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
