# Research Vault

An AI-powered research assistant that extracts structured insights from papers and enables cross-document synthesis through natural language queries.

## Overview

Research Vault transforms unstructured research content (PDFs, articles, notes) into a queryable knowledge base. Unlike traditional RAG systems that chunk and retrieve raw text, Research Vault extracts **discrete insights** with structured metadata, enabling true cross-paper synthesis.

## Core Features

- **Ingest** research papers (PDF or text)
- **Extract** structured insights (Claim, Evidence, Context)
- **Store** in hybrid database (relational + vector)
- **Query** with natural language across your entire library
- **Synthesize** cross-document insights with source attribution

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, LangGraph |
| Frontend | Next.js 16, React 19, TypeScript |
| Database | SQLite (MVP) → PostgreSQL |
| Vector Store | Qdrant |
| LLM | Claude (Anthropic) |
| Embeddings | OpenAI text-embedding-3-small |

## Status

🚧 **Under Development** - Not ready for production use.

## Quick Start

*Coming soon - see [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) once available.*

## Documentation

- [Requirements](REQUIREMENTS.md) - Functional and non-functional specs
- [Architecture](docs/ARCHITECTURE.md) - System design and flows
- [Domain Model](docs/DOMAIN_MODEL.md) - Entity schemas
- [Operations](docs/OPERATIONS.md) - Deployment and troubleshooting
- [Contributing](CONTRIBUTING.md) - How to contribute

## License

MIT License - see [LICENSE](LICENSE) for details.
