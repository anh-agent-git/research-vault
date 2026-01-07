# Research Vault

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

---

**Keywords:** agentic ai, llm rag, rag system, vector database, semantic search, knowledge base, research tool, paper management, structured extraction, langchain, langgraph, ai agent, llm orchestration, python fastapi, anthropic claude
