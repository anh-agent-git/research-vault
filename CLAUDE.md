# Research Vault

## Overview

An AI research assistant that ingests papers/articles, extracts structured research patterns, stores them in a searchable knowledge base, and answers cross-paper questions through synthesis—not summarization.

## Problem Statement

Research insights are fragmented across PDFs, notes, and memory. There is no cumulative system that converts reading into a structured, queryable body of knowledge that compounds over time.

## The Pattern Schema

Research Vault extracts structured patterns with three core components:

### Claim
The main insight, assertion, or finding from the source material.

**Key question:** What is the author claiming or demonstrating?

### Evidence
Supporting quotes, examples, data, or cases from the source.

**Key question:** What proof or examples support this claim?

### Context
Surrounding context, implications, limitations, or connections to other ideas.

**Key question:** Why does this matter? What are the boundaries?

### Additional Fields

| Field | Description |
|-------|-------------|
| `name` | Short name (3-6 words) |
| `tags` | Flexible categorization (e.g., "methodology", "finding", "limitation") |
| `custom_fields` | JSON for future extensibility |

## Core Capabilities

1. **Ingest** research content (PDF or text)
2. **Extract** structured patterns (Claim, Evidence, Context)
3. **Persist** patterns and paper metadata in a hybrid store (semantic + structured)
4. **Query** across the full library with natural language
5. **Synthesize** patterns (themes, agreements, contradictions) grounded in stored data
6. **Detect** relationships and conflicts between patterns

## Patterns as First-Class Entities

Unlike traditional RAG systems that chunk and retrieve raw text, this system extracts **structured patterns**—discrete findings with Claim/Evidence/Context attribution, source metadata, and semantic embeddings. This enables true cross-paper synthesis.

## Target User

Single expert user optimizing for depth of understanding, synthesis, and long-term knowledge accumulation.

## Success Criteria

The system should answer questions like:

- "What patterns recur across papers about agent memory limitations?"
- "Where do authors disagree on whether tool use reduces hallucinations?"
- "Synthesize what I've learned about prompt engineering, with references to extracted patterns."

Answers must be **grounded in stored patterns and metadata**, not only the current prompt context.

## Why Build This

- Portfolio-grade agentic system (orchestration, memory, tooling)
- Practical research workflow and pattern extraction engine
- Open-source alternative to proprietary research tools

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12, Node.js 20.x |
| LLM | Claude (Anthropic API) |
| Embeddings | OpenAI text-embedding-3-small |
| Orchestration | LangGraph 1.0 + LangSmith |
| Vector DB | Qdrant 1.16.x |
| Relational DB | SQLite (MVP) → PostgreSQL |
| Backend | FastAPI 0.128.x |
| Frontend | Next.js 16.x |
| PDF Parsing | PyMuPDF 1.26.x |

---

## Documentation Structure

```
research-vault/
├── CLAUDE.md                    # This file - project overview
├── PLAN.md                      # High-level implementation tracker
├── REQUIREMENTS.md              # Functional & non-functional requirements
├── CONTRIBUTING.md              # How to contribute
├── docs/
│   ├── ARCHITECTURE.md          # System architecture (C4 diagrams, flows, risks)
│   ├── DOMAIN_MODEL.md          # Entity relationships, lifecycles, schemas
│   ├── OPERATIONS.md            # Setup, deployment, troubleshooting runbook
│   ├── GETTING_STARTED.md       # User onboarding guide
│   ├── BACKLOG.md               # Feature planning
│   └── devlog/                  # Detailed implementation logs
│       ├── phase-0-setup.md
│       ├── phase-1-specification.md
│       ├── phase-2-infrastructure.md
│       └── ...
├── backend/
│   └── CLAUDE.md                # Backend-specific context
└── frontend/
    └── CLAUDE.md                # Frontend-specific context
```

---

## Engineer Instructions

**READ THIS FIRST** when starting a new session. These are standing instructions for any engineer (human or AI) working on this project.

### Starting a New Session

1. **Read context files in this order:**
   - `CLAUDE.md` (this file) — project overview
   - `PLAN.md` — current progress, what phase we're in
   - `docs/devlog/phase-X-*.md` — detailed log for current phase
   - `docs/*.md` — architecture docs as needed:
     - `ARCHITECTURE.md` — C4 diagrams, sequence flows, risks
     - `DOMAIN_MODEL.md` — entity relationships, lifecycles, schemas
     - `OPERATIONS.md` — setup, deployment, troubleshooting
   - `backend/CLAUDE.md` or `frontend/CLAUDE.md` — if working on that area

2. **Check for open questions** in the current phase's devlog

3. **Resume work** from where the last session left off

### After Completing Work

**You MUST update these files after every implementation session:**

| File | What to Update | When |
|------|----------------|------|
| `PLAN.md` | Task status (⬜→🟡→✅), progress counts | After completing any task |
| `docs/devlog/phase-X-*.md` | What/Why/How details, session log entry | After every session |
| `backend/CLAUDE.md` | Key patterns, new files, conventions | When backend code changes |
| `frontend/CLAUDE.md` | Key patterns, new files, conventions | When frontend code changes |
| `PLAN.md` Decision Log | Any significant technical decisions | When making architecture choices |

### Devlog Update Template

Add this to the current phase's devlog after each session:

```markdown
## Session Log

| Date | Engineer | What Changed |
|------|----------|--------------|
| YYYY-MM-DD | Claude/Human | Brief description of work done |

## What We Did
- Completed X
- Implemented Y
- Fixed Z

## How We Did It
- Used pattern A because...
- Key command: `...`

## Open Questions / Next Steps
- Still need to...
- Blocked on...
```

### Commit Conventions

When committing changes:

1. **Stage related files together** (don't mix unrelated changes)
2. **Commit message format:**
   ```
   [Phase X] Brief description

   - Detail 1
   - Detail 2

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```
3. **Push after significant milestones**, not every small change
4. **No commits without explicit user approval**

### Key Principles

1. **Update docs as you go** — don't batch documentation updates
2. **Log decisions with rationale** — future sessions need to understand "why"
3. **Keep devlogs detailed** — they are the primary context for session continuity
4. **Update CLAUDE.md files** — when patterns or conventions change

---

## Execution Control (Applies to Claude and humans)

### Slice-based execution is mandatory
- Plans must be broken into SLICES (1–3 tasks each).
- After plan approval, implement ONLY the next slice.

### Hard stop + approval gates
After completing a slice, you MUST stop and request approval before continuing.

At the end of each slice, provide:
1) Files changed (with purpose)
2) Tests added/updated and how to run them
3) Any decisions made + rationale
4) Risks / open questions
5) Next slice scope
6) Ask: "Proceed to next slice?"

### Scope guardrails
- No drive-by refactors outside the slice.
- No expanding scope based on "while I'm here."
- If an ambiguity is discovered, STOP and ask before implementing.

---

## Development Notes

### Common Commands

```bash
# Backend
cd backend
uv sync                              # Install dependencies
uv run alembic upgrade head          # Run database migrations
uv run uvicorn app.main:app --reload # Start server on :8000
uv run ruff check .                  # Lint
uv run ruff format .                 # Format
uv run pytest                        # Run tests

# Frontend
cd frontend
npm install                          # Install dependencies
npm run dev                          # Start dev server on :3000
npm run build                        # Production build
npm run lint                         # ESLint

# Docker
docker compose up qdrant             # Start Qdrant on :6333
docker compose up                    # Start full stack
docker compose down                  # Stop all services
```

### Gotchas

| Issue | Solution |
|-------|----------|
| `docker-compose` not found | Use `docker compose` (v2, with space) instead of `docker-compose` (v1, deprecated) |
| `uv run` not finding packages | Run from `backend/` directory where `.venv` exists |
| Frontend build fails | Check Node version is 20.x (`node --version`) |

---

## Migration Context

This project was migrated from a private codebase. Reference materials:

- **Source repo:** `research-assistant` (private)
- **Migration plan:** `plan-oss.md` in source repo

### Key Differences from Source

| Aspect | Source (research-assistant) | This Repo (research-vault) |
|--------|----------------------------|---------------------------|
| Extraction schema | SRAL (State, Reason, Act, Learn) | Claim, Evidence, Context |
| Domain-specific | Yes (SRAL framework) | Generic research patterns |
| Filters | SRAL component filters | Tag-based filters |
| Pattern fields | `state_content`, `reason_content`, `act_content`, `learn_content` | `claim`, `evidence`, `context` |

### Files NOT copied from source

- `**/sral_*` - SRAL-specific code
- `**/pattern_extractor_v2.py` - SRAL-specific extractor
- `docs/devlog/phase-9-*` - SRAL extraction improvements
- Any file with hardcoded personal paths
