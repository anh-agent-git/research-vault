# Research Vault

An AI-powered research assistant that extracts structured patterns from papers and enables cross-document synthesis through natural language queries.

## Overview

Research Vault transforms unstructured research content (PDFs, articles, notes) into a queryable knowledge base. Unlike traditional RAG systems that chunk and retrieve raw text, Research Vault extracts **discrete patterns** with structured metadata, enabling true cross-paper synthesis.

## Core Features

- **Ingest** research papers (PDF or text)
- **Extract** structured patterns (Claim, Evidence, Context)
- **Store** in hybrid database (relational + vector)
- **Query** with natural language across your entire library
- **Synthesize** cross-document patterns with source attribution

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

🔬 **Beta** - Functional for personal research workflows. Contributions welcome!

## Design Notes

- **Single-user system** - Designed for individual researchers
- **Local-first** - All data stored on your machine, no cloud dependency
- **Extensible** - Fork and customize for your research needs

## Quick Start

See [Getting Started](docs/GETTING_STARTED.md) for detailed setup instructions.

**TL;DR:**
```bash
git clone https://github.com/aakashsharan/research-vault.git
cd research-vault
cp .env.example .env  # Add your API keys
docker compose up --build
```

Open http://localhost:3000 to start uploading papers.

## Documentation

- [Requirements](REQUIREMENTS.md) - Functional and non-functional specs
- [Architecture](docs/ARCHITECTURE.md) - System design and flows
- [Domain Model](docs/DOMAIN_MODEL.md) - Entity schemas
- [Operations](docs/OPERATIONS.md) - Deployment and troubleshooting
- [Contributing](CONTRIBUTING.md) - How to contribute

## License

MIT License - see [LICENSE](LICENSE) for details.
