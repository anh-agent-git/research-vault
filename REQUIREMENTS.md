# Requirements

## Functional Requirements

### FR-1: Paper Ingestion

| ID | Requirement |
|----|-------------|
| FR-1.1 | System shall accept PDF file uploads via web UI |
| FR-1.2 | System shall accept plain text input via web UI |
| FR-1.3 | System shall extract and store paper metadata: title, authors, date, source, published date, type |
| FR-1.4 | System shall support paper types: research paper, blog post, article, technical report, book chapter |

### FR-2: Pattern Extraction

| ID | Requirement |
|----|-------------|
| FR-2.1 | System shall extract patterns from ingested papers using the Claim/Evidence/Context schema |
| FR-2.2 | System shall support partial patterns (e.g., Claim only, Claim+Evidence without Context) |
| FR-2.3 | Each pattern shall have a short name (3-6 words) for identification |
| FR-2.4 | System shall present extracted patterns for user review before persisting |
| FR-2.5 | Patterns shall support flexible tags for categorization (e.g., "methodology", "finding", "limitation") |
| FR-2.6 | Patterns shall support a JSON custom_fields column for future extensibility |

### FR-3: Pattern Review & Editing

| ID | Requirement |
|----|-------------|
| FR-3.1 | System shall display all extracted patterns for review after extraction |
| FR-3.2 | User shall be able to approve or reject each extracted pattern |
| FR-3.3 | User shall be able to edit patterns after they have been saved |
| FR-3.4 | User shall be able to edit the claim, evidence, context, name, and tags of a pattern |

### FR-4: Library Management

| ID | Requirement |
|----|-------------|
| FR-4.1 | User shall be able to browse all papers in the library |
| FR-4.2 | User shall be able to filter papers by: date, type, source |
| FR-4.3 | User shall be able to view all patterns associated with a specific paper |
| FR-4.4 | User shall be able to archive papers (hidden from queries, recoverable) |
| FR-4.5 | User shall be able to permanently delete papers and their associated patterns |
| FR-4.6 | User shall be able to delete individual patterns |

### FR-5: Querying & Synthesis

| ID | Requirement |
|----|-------------|
| FR-5.1 | System shall provide a web-based query interface |
| FR-5.2 | System shall support natural language queries across the pattern library |
| FR-5.3 | System shall support scoped queries filtered by: date, type, source, tags |
| FR-5.4 | System shall synthesize responses grounded in stored patterns, not just prompt context |
| FR-5.5 | System shall format responses as bulleted patterns or other formats as appropriate to the query |
| FR-5.6 | System shall maintain conversation history within a browser session |
| FR-5.7 | Conversation history shall not persist beyond the browser session |

### FR-6: Authentication & Access

| ID | Requirement |
|----|-------------|
| FR-6.1 | System shall run locally with no authentication required |
| FR-6.2 | System shall support a single user |

---

## MVP Scope

### In Scope

1. Upload paper (PDF or plain text)
2. Extract patterns using Claim/Evidence/Context schema
3. Review and approve/reject extracted patterns
4. Save approved patterns to knowledge base
5. Query against stored patterns with scoped filters
6. Session-based conversation history

### Out of Scope (Deferred)

- Conflict/relationship detection between patterns
- Multi-user support
- Export functionality
- Automatic pattern extraction (without review)
- Persistent conversation history across sessions
- Custom extraction templates (configurable prompts)

---

## User Workflows

### Primary Workflow: Ingest Paper

```
User uploads PDF/text
    -> System extracts metadata
    -> System extracts patterns (Claim/Evidence/Context)
    -> User reviews patterns (approve/reject each)
    -> Approved patterns saved to knowledge base
```

### Primary Workflow: Query Library

```
User enters natural language query
    -> User optionally applies scope filters (date, type, source, tags)
    -> System retrieves relevant patterns
    -> System synthesizes response grounded in patterns
    -> User can ask follow-up questions (session context maintained)
```

### Secondary Workflow: Manage Library

```
User browses papers (with filters)
    -> User can view patterns for any paper
    -> User can edit, delete patterns
    -> User can archive or delete papers
```

---

## Non-Functional Requirements

### NFR-1: Performance

| ID | Requirement |
|----|-------------|
| NFR-1.1 | System shall support PDF files up to 50 pages |
| NFR-1.2 | Pattern extraction may take up to 2 minutes for a 20-page paper |
| NFR-1.3 | Synthesis queries shall respond in under 10 seconds |
| NFR-1.4 | Simple pattern lookups shall respond in under 3 seconds |

### NFR-2: Scale & Storage

| ID | Requirement |
|----|-------------|
| NFR-2.1 | System shall support a library of 1,000+ papers |
| NFR-2.2 | System shall support 5,000-20,000+ patterns (5-20 patterns per paper) |
| NFR-2.3 | System shall use a local vector database for pattern storage and retrieval |
| NFR-2.4 | Data shall persist locally (cloud migration planned post-MVP) |

### NFR-3: Deployment & Environment

| ID | Requirement |
|----|-------------|
| NFR-3.1 | System shall run locally on macOS |
| NFR-3.2 | System shall be deployable via Docker container |
| NFR-3.3 | App and data run locally; LLM API calls require internet connection |
| NFR-3.4 | Cross-platform support deferred to post-MVP |
| NFR-3.5 | Cloud VM deployment deferred to post-MVP |
| NFR-3.6 | Local LLM support (fully offline) deferred to post-MVP |

### NFR-4: Reliability & Error Handling

| ID | Requirement |
|----|-------------|
| NFR-4.1 | Failed extraction shall rollback all changes; user must re-upload |
| NFR-4.2 | LLM failures shall retry with exponential backoff (1s -> 2s -> 4s with jitter) |
| NFR-4.3 | After 3 failed retries, system shall surface error to user with manual retry option |

### NFR-5: Usability & Compatibility

| ID | Requirement |
|----|-------------|
| NFR-5.1 | System shall support modern browsers (Chrome, Firefox, Safari) |
| NFR-5.2 | System shall be optimized for desktop browsers only |
| NFR-5.3 | Mobile browser support deferred to post-MVP |

---

## Technology Stack

### Overview

| Layer | Technology | Version | Notes |
|-------|------------|---------|-------|
| Language | Python | 3.12 | Primary backend language |
| Frontend Runtime | Node.js | 20.x LTS | Next.js runtime |
| LLM | Claude (Anthropic API) | claude-3-5-sonnet | Pattern extraction and synthesis |
| Embeddings | OpenAI | text-embedding-3-small | 1536 dimensions, semantic search |
| Orchestration | LangGraph | 1.0.x | Workflow orchestration (stable v1) |
| Observability | LangSmith | latest | Tracing and debugging |
| Vector DB | Qdrant | 1.16.x | Local-first, cloud migration path |
| Relational DB | SQLite -> Postgres | SQLite 3.x | SQLite for MVP, Postgres for cloud |
| Backend | FastAPI | 0.128.x | REST API server |
| ORM | SQLAlchemy | 2.0.x | Database ORM |
| Validation | Pydantic | 2.12.x | Request/response schemas |
| Frontend | Next.js | 16.x | React-based web UI |
| Styling | Tailwind CSS | 4.x | Utility-first CSS (v4 rewrite) |
| PDF Parsing | PyMuPDF | 1.26.x | Text extraction from PDFs |

### Technology Decisions & Rationale

#### LangGraph over LangChain
- Supports stateful, multi-step workflows with cycles
- Better for complex extraction/synthesis pipelines
- Learning investment for more advanced agent architectures

#### Qdrant over alternatives
- **vs Pinecone**: Qdrant runs locally (Pinecone is cloud-only)
- **vs Chroma**: Qdrant has better filtering, more production-ready
- **vs Weaviate**: Qdrant is lighter, simpler setup, sufficient for our needs
- Supports metadata filtering (for scoped queries by date, type, tags)
- Clear cloud migration path (Qdrant Cloud)

#### FastAPI + Next.js over Streamlit/Gradio
- Decoupled architecture: API and UI evolve independently
- More customizable UI for library management, pattern editing, scoped queries
- Production-ready, scales beyond MVP

#### PyMuPDF for PDF parsing
- Fast and reliable for most academic PDFs
- Extracts text with layout preservation
- Can add pdfplumber or Claude vision for complex layouts if needed

### Post-MVP Technology Additions

| Technology | Purpose | When |
|------------|---------|------|
| Postgres | Replace SQLite for cloud deployment | Cloud migration |
| Qdrant Cloud | Managed vector DB | Cloud migration |
| Local LLM (Ollama) | Fully offline operation | Post-MVP |
| Docker Compose | Multi-container orchestration | Production deployment |
