# Phase 1: Specification

## Goal

Write specs before any code (spec-driven development).

## Outcome

Complete requirements and domain model documentation.

---

## Session Log

| Date | Engineer | What Changed |
|------|----------|--------------|
| 2025-01-05 | Claude | Created REQUIREMENTS.md with functional/non-functional specs |
| 2025-01-05 | Claude Opus 4.5 | Created DOMAIN_MODEL.md and API_SPEC.md |

---

## What We Did

### Slice 1: Requirements (completed in Phase 0)
- Created REQUIREMENTS.md with:
  - Functional requirements (FR-1 through FR-6)
  - MVP scope definition
  - User workflows
  - Non-functional requirements (performance, scale, deployment)
  - Technology stack with rationale

### Slice 2: Domain Model & API Spec
- Created docs/DOMAIN_MODEL.md with:
  - Entity-relationship diagram (Paper, Pattern, Embedding, Session)
  - Core entity definitions with field specs
  - Enums (PaperType, PaperStatus, PatternStatus)
  - Entity lifecycle state diagrams
  - Aggregate boundaries
  - Validation rules
  - Database schema (SQL)
  - Qdrant collection schema

- Created docs/API_SPEC.md with:
  - Health check endpoint
  - Paper endpoints (upload, list, get, delete, review)
  - Pattern endpoints (update, delete)
  - Query endpoints (query, follow-up)
  - Session behavior and limits
  - Error response formats
  - Pagination patterns

---

## How We Did It

- Adapted domain model from source repo (research-assistant)
- Replaced SRAL schema with Claim/Evidence/Context
- Kept "Pattern" entity name (as per plan-oss.md)
- Added tags and custom_fields for extensibility
- Defined clear API contracts before implementation

---

## Files Created

```
docs/
├── DOMAIN_MODEL.md     # Entity schemas, relationships, lifecycles
├── API_SPEC.md         # REST endpoint contracts
└── devlog/
    └── phase-1-specification.md  # This file

REQUIREMENTS.md         # Functional & non-functional requirements (created in Phase 0)
```

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Keep "Pattern" entity name | Matches plan-oss.md specification |
| Add tags as JSON array | Flexible categorization without schema changes |
| Add custom_fields JSON | Future extensibility without migrations |
| At least one of claim/evidence/context required | Partial patterns are valid (e.g., just a claim) |
| Session-based query history | No persistent history, simpler MVP |

---

## Open Questions / Next Steps

- Ready for Phase 2: Infrastructure Migration
- Next: Set up Python backend with FastAPI, database, and services
