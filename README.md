# Research Vault
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

An **agentic AI** research assistant that extracts structured patterns from papers and enables cross-document synthesis through natural language queries. Built with **LLM orchestration**, **RAG (Retrieval-Augmented Generation)**, and **vector search**.

## Overview

Research Vault transforms unstructured research content (PDFs, articles, notes) into a queryable **knowledge base**. Unlike traditional **RAG systems** that chunk and retrieve raw text, Research Vault uses **structured extraction** to pull discrete patterns with metadata, enabling true cross-paper synthesis.

**Key differentiator:** Instead of retrieving text chunks, Research Vault extracts *findings* (Claim → Evidence → Context) and synthesizes answers across your entire library with citations.

## Why I Built This

I was drowning in research papers. I'd read something important, forget where I saw it, and spend hours searching through PDFs.

Existing tools didn't cut it. Note-taking apps require too much manual effort. Tools like NotebookLM are great for Q&A but don't extract structured patterns I can query later. Traditional RAG systems just return text chunks without real synthesis.

I didn't want to manually organize my research—I wanted a system that does it for me. So I built Research Vault. It automatically extracts structured insights from papers, stores them locally, and lets me ask questions like "where do authors disagree about agent memory?" and get synthesized answers with citations.

This is an open-source version of my personal tool, simplified for others facing the same problem.

## Core Features

- **Ingest** research papers (PDF or text)
- **Extract** structured patterns (Claim, Evidence, Context)
- **Store** in hybrid database (relational + vector)
- **Query** with natural language across your entire library
- **Synthesize** cross-document patterns with source attribution

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI |
| LLM Orchestration | LangGraph, LangChain |
| Frontend | Next.js 16, React 19, TypeScript |
| Database | SQLite (MVP) → PostgreSQL |
| Vector Database | Qdrant (semantic search) |
| LLM | Claude (Anthropic API) |
| Embeddings | OpenAI text-embedding-3-small |

**Architecture highlights:**
- **Agentic workflow** with multi-step LLM orchestration
- **Hybrid RAG** combining relational + vector storage
- **3-pass extraction** pipeline with citation verification
- **Async Python** throughout (aiosqlite, async clients)

## Status

✅ **Production-ready for personal use** - Beta for multi-user features

- **619 backend tests** + **23 frontend tests**
- **7 comprehensive docs** (Architecture, API, Operations, etc.)
- **Docker deployment** with health checks
- **CI/CD pipeline** (linting, testing, building)


**Contributions welcome!** See [CONTRIBUTING.md](CONTRIBUTING.md)

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

Open http://localhost:3000

### What You'll See
1. **Upload page** - Drop a PDF or paste text
2. **Review page** - Approve/reject extracted patterns
3. **Library page** - Browse your knowledge base
4. **Query page** - Ask questions, get synthesized answers

## Production Features

Research Vault isn't just a demo—it's built for daily use:

- ✅ **Partial success handling** - Paper saved even if extraction fails
- ✅ **Graceful degradation** - Continues working if vector DB is unavailable
- ✅ **Retry logic** - LLM calls retry with exponential backoff
- ✅ **Error boundaries** - Frontend handles API failures gracefully
- ✅ **Health checks** - `/health` endpoint monitors all dependencies
- ✅ **Comprehensive logging** - Debug production issues easily
- ✅ **Integration tests** - Full pipeline tested end-to-end
- ✅ Security scanning - Pre-commit hooks prevent secret leaks

See [OPERATIONS.md](docs/OPERATIONS.md) for deployment and troubleshooting.

## Documentation

- [Requirements](REQUIREMENTS.md) - Functional and non-functional specs
- [Architecture](docs/ARCHITECTURE.md) - System design and flows
- [Domain Model](docs/DOMAIN_MODEL.md) - Entity schemas
- [Operations](docs/OPERATIONS.md) - Deployment and troubleshooting
- [Contributing](CONTRIBUTING.md) - How to contribute

## Community & Support

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/aakashsharan/research-vault/issues)
- 📖 **Documentation:** [docs/](docs/)
- 🤝 **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)

**Built by [@aakashsharan](https://github.com/aakashsharan)** - Applying 12+ years of distributed systems experience to agentic AI challenges.

## Related Work

Research Vault builds on ideas from:
- **ReAct** (Yao et al.) - Interleaving reasoning and action
- **NotebookLM** - Excellent Q&A over documents, different approach to synthesis
- **Obsidian/Roam** - Graph-based note-taking, manual organization
- **Zotero/Mendeley** - Reference management, no LLM synthesis

See [SRAL Framework Paper](SRAL_Framework_Paper.pdf) for the evaluation framework that inspired this work.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Keywords:** agentic ai, llm rag, rag system, vector database, semantic search, knowledge base, research tool, paper management, structured extraction, langchain, langgraph, ai agent, llm orchestration, python fastapi, anthropic claude
