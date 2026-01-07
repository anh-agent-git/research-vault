# Architecture

This document describes the system architecture, data flows, and key technical decisions for Research Vault.

## Table of Contents

- [System Overview](#system-overview)
- [Container Architecture](#container-architecture)
- [Component Architecture](#component-architecture)
- [Data Flows](#data-flows)
- [Technology Decisions](#technology-decisions)
- [Security Considerations](#security-considerations)

---

## System Overview

Research Vault is an AI-powered research assistant that extracts structured patterns from academic papers and enables semantic querying across your knowledge base.

### Context Diagram (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────────┐
│                           External Systems                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   Anthropic  │    │    OpenAI    │    │  LangSmith   │          │
│  │   Claude API │    │ Embeddings   │    │  (optional)  │          │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │
│         │                   │                   │                   │
└─────────┼───────────────────┼───────────────────┼───────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Research Vault                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │   Ingests papers → Extracts patterns → Enables semantic       │  │
│  │   queries across your research knowledge base                 │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
          ▲
          │
┌─────────┴───────────────────────────────────────────────────────────┐
│                           Researcher                                 │
│                                                                      │
│   - Uploads PDFs or pastes text                                     │
│   - Reviews extracted patterns                                       │
│   - Queries knowledge base                                          │
│   - Manages library                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Actors

| Actor | Description |
|-------|-------------|
| Researcher | Single expert user building a personal knowledge base |
| Anthropic Claude | LLM for metadata extraction, pattern extraction, and synthesis |
| OpenAI | Embedding model for semantic search (text-embedding-3-small) |
| LangSmith | Optional observability platform for debugging LLM calls |

---

## Container Architecture

### Container Diagram (C4 Level 2)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Research Vault                                │
│                                                                      │
│  ┌─────────────────┐      ┌─────────────────┐                       │
│  │    Frontend     │      │     Backend     │                       │
│  │   (Next.js)     │─────▶│    (FastAPI)    │                       │
│  │                 │ REST │                 │                       │
│  │   Port: 3000    │      │   Port: 8000    │                       │
│  └─────────────────┘      └────────┬────────┘                       │
│                                    │                                 │
│                         ┌──────────┼──────────┐                     │
│                         │          │          │                     │
│                         ▼          ▼          ▼                     │
│              ┌──────────────┐ ┌──────────┐ ┌──────────────┐        │
│              │    SQLite    │ │  Qdrant  │ │ External APIs│        │
│              │  (Relational)│ │ (Vector) │ │ (LLM, Embed) │        │
│              │              │ │          │ │              │        │
│              │  Port: N/A   │ │Port: 6333│ │   HTTPS      │        │
│              └──────────────┘ └──────────┘ └──────────────┘        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Container Descriptions

| Container | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Next.js 16, React 19, Tailwind v4 | Web UI for upload, review, library, query |
| Backend | FastAPI 0.128, Python 3.12 | REST API, orchestration, business logic |
| SQLite | SQLite 3 + aiosqlite | Relational storage for papers and patterns |
| Qdrant | Qdrant 1.16 | Vector storage for semantic search |

### Communication

| From | To | Protocol | Purpose |
|------|-----|----------|---------|
| Frontend | Backend | HTTP/REST | All API calls |
| Backend | SQLite | File I/O | Paper/pattern CRUD |
| Backend | Qdrant | HTTP | Vector upsert/search |
| Backend | Anthropic | HTTPS | LLM completions |
| Backend | OpenAI | HTTPS | Embeddings |

---

## Component Architecture

### Backend Components (C4 Level 3)

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Backend                                    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                        Routers                               │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │    │
│  │  │  Papers  │  │ Patterns │  │  Query   │  │  Health  │    │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘    │    │
│  └───────┼─────────────┼─────────────┼─────────────────────────┘    │
│          │             │             │                               │
│          ▼             ▼             ▼                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                       Workflows                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │    │
│  │  │  Ingestion   │  │    Review    │  │    Query     │       │    │
│  │  │  Workflow    │  │   Workflow   │  │   Workflow   │       │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │    │
│  └─────────┼─────────────────┼─────────────────┼────────────────┘    │
│            │                 │                 │                     │
│            ▼                 ▼                 ▼                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                        Services                              │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐ │    │
│  │  │ PDFParser  │ │  Metadata  │ │  Pattern   │ │ Embedding│ │    │
│  │  │  Service   │ │ Extractor  │ │ Extractor  │ │ Service  │ │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────┘ │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐              │    │
│  │  │ LLMClient  │ │VectorStore │ │  Session   │              │    │
│  │  │            │ │  Service   │ │  Manager   │              │    │
│  │  └────────────┘ └────────────┘ └────────────┘              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                     Data Layer                               │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │    │
│  │  │   Models   │  │  Schemas   │  │    DB      │             │    │
│  │  │Paper,Pattern│ │ Pydantic   │  │  Session   │             │    │
│  │  └────────────┘  └────────────┘  └────────────┘             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**Routers** (thin HTTP layer):
| Router | Endpoints | Purpose |
|--------|-----------|---------|
| Papers | `/api/papers/*` | Paper CRUD, upload |
| Patterns | `/api/papers/*/patterns`, `/api/patterns/*` | Pattern review, update |
| Query | `/api/query/*` | Query and follow-up |
| Health | `/health` | System health check |

**Workflows** (orchestration):
| Workflow | Responsibility |
|----------|----------------|
| Ingestion | PDF → Parse → Metadata → Paper → Patterns |
| Review | Decisions → Embed → Upsert → Status update |
| Query | Embed query → Search → Retrieve → Synthesize |

**Services** (business logic):
| Service | Responsibility |
|---------|----------------|
| PDFParserService | Extract text from PDFs (PyMuPDF) |
| MetadataExtractor | LLM-based paper metadata extraction |
| PatternExtractor | 3-pass evidence-anchored pattern extraction |
| EmbeddingService | Generate embeddings (OpenAI) |
| LLMClient | Anthropic Claude API wrapper with retry |
| VectorStoreService | Qdrant operations |
| SessionManager | In-memory conversation session management |

---

## Data Flows

### Ingestion Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Upload  │     │   Parse  │     │ Extract  │     │  Create  │
│  PDF/Text│────▶│   PDF    │────▶│ Metadata │────▶│  Paper   │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                                                        ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Return  │     │  Create  │     │  Verify  │     │ Extract  │
│ Response │◀────│ Patterns │◀────│ Citations│◀────│ Patterns │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                (status: pending)

3-Pass Pattern Extraction:
┌─────────────────────────────────────────────────────────────────┐
│ Pass 1 (Haiku): Extract evidence inventory with [E#] markers   │
│ Pass 2 (Sonnet): Extract patterns with [E#] citations          │
│ Pass 3 (Haiku): Verify citation accuracy                       │
└─────────────────────────────────────────────────────────────────┘
```

### Review Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Review  │     │  Process │     │ Generate │     │  Upsert  │
│ Decisions│────▶│ Approved │────▶│ Embedding│────▶│  Qdrant  │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                                                        ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Return  │     │  Update  │     │  Update  │     │ Process  │
│  Counts  │◀────│  Paper   │◀────│ Pattern  │◀────│ Rejected │
└──────────┘     │  Status  │     │ Statuses │     └──────────┘
                └──────────┘     └──────────┘
                (if all reviewed)

Status Transitions:
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│    pending     │────▶│    approved    │     │    rejected    │
│   (initial)    │     │  (in Qdrant)   │     │  (discarded)   │
└────────────────┘     └────────────────┘     └────────────────┘
```

### Query Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Query   │     │  Create/ │     │  Embed   │     │  Search  │
│  Text    │────▶│  Get     │────▶│  Query   │────▶│  Qdrant  │
└──────────┘     │ Session  │     └──────────┘     └────┬─────┘
                └──────────┘                            │
                                                        ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Return  │     │  Update  │     │Synthesize│     │ Retrieve │
│ Response │◀────│ Session  │◀────│  Answer  │◀────│ Patterns │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                  (Claude with
                                   [P:id] citations)

Session Management:
┌─────────────────────────────────────────────────────────────────┐
│ Sessions stored in-memory with TTL (30 min default)            │
│ Follow-up queries include conversation history for context     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Decisions

### Why These Technologies?

| Technology | Decision | Rationale |
|------------|----------|-----------|
| **FastAPI** | Backend framework | Async support, automatic OpenAPI docs, Pydantic integration |
| **SQLite** | Relational DB (MVP) | Zero setup, file-based, sufficient for single-user |
| **Qdrant** | Vector DB | Open-source, good Python client, self-hostable |
| **Claude** | LLM | Best-in-class for structured extraction, long context |
| **OpenAI Embeddings** | Embeddings | Cost-effective, good quality, 1536 dimensions |
| **Next.js** | Frontend | React ecosystem, App Router, server components |
| **Tailwind CSS** | Styling | Rapid development, consistent design |

### Pattern Extraction Strategy

**3-Pass Evidence-Anchored Extraction:**

| Pass | Model | Purpose |
|------|-------|---------|
| 1 | Haiku | Extract evidence inventory with `[E#]` markers |
| 2 | Sonnet | Extract patterns citing evidence `[E1]`, `[E2]` |
| 3 | Haiku | Verify citations exist and are accurate |

**Rationale:**
- Grounds patterns in source evidence
- Reduces hallucination through citation verification
- Uses cheaper model (Haiku) for mechanical tasks
- Uses smarter model (Sonnet) for nuanced extraction

### Document Chunking (Large Papers)

For documents exceeding 40,000 tokens, the system uses chunked extraction:

| Phase | Description |
|-------|-------------|
| Phase A | Extract patterns from each chunk (Pass 1 + 2) |
| Phase B | Verify citations per chunk (Pass 3) |
| Phase C | Synthesis pass for cross-chunk deduplication |

This enables handling of large papers (up to 200 pages) without context window limits while maintaining citation accuracy.

### Data Model Design

**Why Patterns as First-Class Entities?**

Traditional RAG systems chunk documents and retrieve raw text. Research Vault extracts **structured patterns** because:

1. **Cross-paper synthesis** - Compare claims across papers
2. **Source attribution** - Every pattern links to its paper
3. **Evidence grounding** - Claims linked to supporting evidence
4. **Semantic search** - Embeddings of structured content, not raw chunks

**Pattern Schema:**
```
Pattern {
  name: string       // Short identifier (3-6 words)
  claim: string      // Main assertion
  evidence: string   // Supporting quotes/data
  context: string    // Limitations, implications
  tags: string[]     // Flexible categorization
}
```

### Session Management

**In-Memory Sessions (MVP):**
- Simple implementation for single-user
- 30-minute TTL for cleanup
- Conversation history for multi-turn queries

**Future:** Redis/database-backed sessions for persistence

---

## Security Considerations

### API Key Protection

| Key | Storage | Access |
|-----|---------|--------|
| ANTHROPIC_API_KEY | Environment variable | Backend only |
| OPENAI_API_KEY | Environment variable | Backend only |
| LANGCHAIN_API_KEY | Environment variable | Backend only (optional) |

**Recommendations:**
- Never commit `.env` files (use `.env.example`)
- Use secrets manager in production
- Rotate keys periodically
- Monitor API usage for anomalies

### Input Validation

| Input | Validation |
|-------|------------|
| PDF uploads | File size limit (10MB), page limit (200) |
| Text input | Non-empty, reasonable length |
| Query strings | Non-empty validation |
| Pattern IDs | UUID format validation |

### CORS Configuration

```python
# Development: Allow localhost frontend only
allow_origins=["http://localhost:3000"]

# Production: Restrict to your frontend domain
allow_origins=["https://your-domain.com"]
```

### Data Privacy

| Data | Storage | Retention |
|------|---------|-----------|
| Papers | SQLite (local) | Until deleted |
| Patterns | SQLite + Qdrant | Until deleted |
| Sessions | In-memory | 30 min TTL |
| API logs | stdout | Container lifecycle |

**Considerations:**
- All data stored locally by default
- No telemetry sent to third parties
- LLM providers receive paper content for processing
- Consider data residency requirements

### Authentication (Future)

Current MVP assumes single trusted user. Future considerations:
- API key authentication for multi-user
- OAuth integration
- Role-based access control

### Deployment Security

| Concern | Recommendation |
|---------|----------------|
| TLS | Use reverse proxy (nginx/Caddy) for HTTPS |
| Network | Don't expose Qdrant/SQLite publicly |
| Containers | Run as non-root user |
| Updates | Keep dependencies updated |
| Secrets | Use environment variables, not config files |
