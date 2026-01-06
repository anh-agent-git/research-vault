# Implementation Plan

## Overview

This document tracks the implementation roadmap for Research Vault. Update status as work progresses.

**Status Legend:**
- ⬜ Not started
- 🟡 In progress
- ✅ Completed
- ⏸️ Blocked/Paused

**Detailed Logs:** Each phase has a detailed devlog at `docs/devlog/phase-X-*.md`

---

## Phase 0: Project Setup

**Goal:** Set up the project skeleton with proper OSS foundations.

**Outcome:** Repository with LICENSE, README, documentation structure, and GitHub configs.

**Status:** ✅ Complete

| Task | Status | Notes |
|------|--------|-------|
| Create GitHub repo | ✅ | `research-vault` (private) |
| Add MIT License | ✅ | |
| Add README.md | ✅ | Project overview |
| Add .gitignore | ✅ | Includes .claude/, papers/, .env |
| Add CONTRIBUTING.md | ✅ | Contribution guidelines |
| Add GitHub issue templates | ✅ | Bug report, feature request |
| Add Dependabot config | ✅ | Python, npm, GH Actions |
| Add pre-commit config | ✅ | Secret detection (detect-secrets, gitleaks) |
| Create directory structure | ✅ | backend/, frontend/, docs/ |
| Add CLAUDE.md | ✅ | Project overview + engineer instructions |
| Add PLAN.md | ✅ | This file |

**Devlog:** [`docs/devlog/phase-0-setup.md`](docs/devlog/phase-0-setup.md)

---

## Phase 1: Specification

**Goal:** Write specs before any code (spec-driven development).

**Outcome:** Complete requirements and domain model documentation.

**Dependencies:** Phase 0 (project structure exists)

**Status:** ✅ Complete

| Task | Status | Notes |
|------|--------|-------|
| Write REQUIREMENTS.md | ✅ | Functional & non-functional requirements |
| Write docs/DOMAIN_MODEL.md | ✅ | Entity relationships, schemas |
| Write docs/API_SPEC.md | ✅ | Endpoint contracts (prose) |

**Devlog:** [`docs/devlog/phase-1-specification.md`](docs/devlog/phase-1-specification.md)

---

## Phase 2: Infrastructure Migration

**Goal:** Migrate core infrastructure from source repo (no business logic yet).

**Outcome:** Backend and frontend scaffolding with database and vector store setup.

**Dependencies:** Phase 1 (specs approved)

**Status:** ✅ Complete

| Task | Status | Notes |
|------|--------|-------|
| Set up Python backend (FastAPI) | ✅ | pyproject.toml, config, main.py |
| Set up database (SQLAlchemy + Alembic) | ✅ | Async SQLite, migrations, health check |
| Set up Qdrant vector store | ✅ | VectorStoreService wrapper |
| Set up PDF parser service | ✅ | PyMuPDF with page limits |
| Set up LLM client service | ✅ | Anthropic SDK with retry |
| Set up session manager | ✅ | In-memory with TTL, cleanup task |
| Set up Next.js frontend | ✅ | Next.js 16, React 19, Tailwind v4 |
| Set up Docker Compose | ✅ | Backend, frontend, Qdrant |
| Set up CI workflow | ✅ | GitHub Actions (ruff, pytest, eslint, build) |

**Devlog:** [`docs/devlog/phase-2-infrastructure.md`](docs/devlog/phase-2-infrastructure.md)

---

## Phase 3: Domain Model Implementation

**Goal:** Implement Paper and Pattern models with new schema.

**Outcome:** Database models, Pydantic schemas, migrations.

**Dependencies:** Phase 2 (infrastructure exists)

**Status:** ✅ Complete

| Task | Status | Notes |
|------|--------|-------|
| Implement Paper model | ✅ | SQLAlchemy model + PaperType/PaperStatus enums (PR #12) |
| Implement Pattern model | ✅ | claim, evidence, context, tags, custom_fields (PR #13) |
| Implement Paper Pydantic schemas | ✅ | PaperMetadataInput, PaperMetadataExtracted, PaperResponse (PR #14) |
| Implement Pattern Pydantic schemas | ✅ | ExtractedPattern, PatternResponse, review schemas (PR #15) |
| Create Alembic migrations | ✅ | Initial schema + CHECK constraint (PR #16, #17) |
| Write tests | ✅ | 65 new tests (TDD approach) |

**Devlog:** [`docs/devlog/phase-3-domain-model.md`](docs/devlog/phase-3-domain-model.md)

---

## Phase 4: Extraction Service

**Goal:** Implement pattern extraction with new Claim/Evidence/Context schema.

**Outcome:** Working extraction prompts and services.

**Dependencies:** Phase 3 (models exist)

**Status:** ✅ Complete

| Task | Status | Notes |
|------|--------|-------|
| Write extraction prompts | ✅ | Evidence inventory, extraction, verification (PRs #19, #20) |
| Implement PatternExtractor service | ✅ | 3-pass evidence-anchored pipeline (PR #21) |
| Implement MetadataExtractor service | ✅ | Paper metadata extraction (PR #19) |
| Implement EmbeddingService | ✅ | OpenAI text-embedding-3-small (PR #21) |
| Write synthesis prompt | ✅ | Pattern context builder, [P:id] citations (PR #22) |
| Write service tests | ✅ | 200 new tests (TDD approach) |

**Devlog:** [`docs/devlog/phase-4-extraction.md`](docs/devlog/phase-4-extraction.md)

---

## Phase 5: Workflows

**Goal:** Implement LangGraph workflows for ingestion, review, and query.

**Outcome:** Working end-to-end pipelines.

**Dependencies:** Phase 4 (services exist)

**Status:** ✅ Complete

| Task | Status | Notes |
|------|--------|-------|
| Implement ingestion workflow | ✅ | Parse → extract_metadata → create paper → extract_patterns → create patterns |
| Implement review workflow | ✅ | Validate → embed approved → upsert to vector store → update status |
| Implement query workflow | ✅ | Get session → embed query → search → retrieve → synthesize → update session |
| Write workflow tests | ✅ | 50 tests (TDD approach) |

**Devlog:** [`docs/devlog/phase-5-workflows.md`](docs/devlog/phase-5-workflows.md)

---

## Phase 6: API Routes

**Goal:** Implement REST API endpoints.

**Outcome:** Full API for papers, patterns, and queries.

**Dependencies:** Phase 5 (workflows exist)

**Status:** ✅ Complete

| Task | Status | Notes |
|------|--------|-------|
| Implement paper routes | ✅ | Upload (PDF/text), list, get, delete (PR #24) |
| Implement pattern routes | ✅ | Review decisions, list, update, delete (PR #24) |
| Implement query routes | ✅ | Query, follow-up with session management (PR #24) |
| Write API tests | ✅ | 44 tests (TDD approach) |

**Devlog:** [`docs/devlog/phase-6-api.md`](docs/devlog/phase-6-api.md)

---

## Phase 7: Frontend

**Goal:** Build the web UI.

**Outcome:** Complete interface for upload, review, library, and query.

**Dependencies:** Phase 6 (API exists)

**Status:** ⬜ Not started

| Task | Status | Notes |
|------|--------|-------|
| Set up TypeScript types | ⬜ | Match API schemas |
| Set up API client | ⬜ | Fetch wrapper |
| Build Upload page | ⬜ | |
| Build Review page | ⬜ | |
| Build Library page | ⬜ | |
| Build Query page | ⬜ | |

**Devlog:** [`docs/devlog/phase-7-frontend.md`](docs/devlog/phase-7-frontend.md)

---

## Phase 8: Integration & Polish

**Goal:** End-to-end testing, documentation, and CI/CD.

**Outcome:** Production-ready system.

**Dependencies:** Phase 7 (full stack exists)

**Status:** ⬜ Not started

| Task | Status | Notes |
|------|--------|-------|
| Write integration tests | ⬜ | Full flow tests |
| Set up GitHub Actions CI | ⬜ | Tests, linting |
| Complete documentation | ⬜ | ARCHITECTURE.md, OPERATIONS.md, etc. |
| Security verification | ⬜ | grep for secrets, paths |
| Final polish | ⬜ | |

**Devlog:** [`docs/devlog/phase-8-polish.md`](docs/devlog/phase-8-polish.md)

---

## Progress Summary

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 0: Setup | ✅ | 11/11 |
| Phase 1: Specification | ✅ | 3/3 |
| Phase 2: Infrastructure | ✅ | 9/9 |
| Phase 3: Domain Model | ✅ | 6/6 |
| Phase 4: Extraction | ✅ | 6/6 |
| Phase 5: Workflows | ✅ | 4/4 |
| Phase 6: API | ✅ | 4/4 |
| Phase 7: Frontend | ⬜ | 0/6 |
| Phase 8: Polish | ⬜ | 0/5 |
| **Total** | 🟡 | **43/54** |

---

## Decision Log

Track key decisions made during implementation:

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-05 | MIT License | Standard permissive OSS license |
| 2025-01-05 | Claim/Evidence/Context schema | Generic alternative to SRAL, applicable to any research domain |
| 2025-01-05 | JSON custom_fields for extensibility | Future-proof without migrations |
| 2025-01-05 | Tag-based filtering | Flexible categorization vs. fixed categories |
| 2025-01-05 | Pre-commit with detect-secrets + gitleaks | Dual-layer secret detection for OSS security |
| 2026-01-06 | 3-pass evidence-anchored extraction | Higher quality through evidence grounding, reproducible results |
| 2026-01-06 | Multi-model strategy (Haiku/Sonnet) | Cost optimization: Haiku for Pass 1/3, Sonnet for Pass 2 |
| 2026-01-06 | Computed verification status override | Consistent status rules, don't trust LLM's self-assessment |
| 2026-01-05 | Simple async functions over LangGraph | Linear pipelines don't need graph complexity; easier testing/debugging |
| 2026-01-05 | Partial success workflow strategy | Continue on non-critical failures (e.g., paper created even if patterns fail) |

---

## Blockers & Risks

| Issue | Impact | Mitigation |
|-------|--------|------------|
| | | |
