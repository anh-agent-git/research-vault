# Phase 3: Domain Model Implementation

## Goal

Implement Paper and Pattern models with new Claim/Evidence/Context schema.

## Outcome

Database models, Pydantic schemas, and Alembic migrations for the core domain entities.

---

## Session Log

| Date | Engineer | What Changed |
|------|----------|--------------|
| 2026-01-05 | Claude Opus 4.5 | Slice 1: Paper model + enums (PR #12) |
| 2026-01-05 | Claude Opus 4.5 | Slice 2: Pattern model + enum (PR #13) |
| 2026-01-05 | Claude Opus 4.5 | Slice 3: Paper Pydantic schemas (PR #14) |

---

## Development Approach

**From scratch, not copy-paste.** Code is written fresh based on:
- OSS specifications (`DOMAIN_MODEL.md`, `API_SPEC.md`, `REQUIREMENTS.md`)
- Non-OSS repo as reference for patterns and structure
- Key difference: **Claim/Evidence/Context** schema instead of SRAL

---

## Slice 1: Paper Model + Enums

**PR:** #12

### What We Did

- Created `PaperType` enum: research_paper, blog_post, article, technical_report, book_chapter
- Created `PaperStatus` enum: processing, ready_for_review, active, archived
- Created `Paper` SQLAlchemy model with:
  - UUID primary key (auto-generated)
  - title (500 chars), authors (JSON list), dates, source (1000 chars)
  - content_text (Text), type, status
  - created_at/updated_at timestamps with auto-update
  - Index on (status, type, published_date)

### Files Created

```
backend/app/models/paper.py          # Paper model + enums
backend/app/models/__init__.py       # Updated exports
backend/tests/test_models/__init__.py
backend/tests/test_models/test_paper.py  # 15 tests
```

### Tests (15)

- Enum values and string inheritance (6)
- Model defaults, persistence, timestamps (9)

---

## Slice 2: Pattern Model + Enum

**PR:** #13

### What We Did

- Created `PatternStatus` enum: pending, approved, rejected
- Created `Pattern` SQLAlchemy model with:
  - UUID primary key
  - FK to papers with CASCADE delete
  - name (200 chars)
  - **claim, evidence, context** (Text, nullable) - the core schema change
  - tags (JSON list), custom_fields (JSON dict) - extensibility
  - embedding_id (100 chars), status
  - created_at/updated_at timestamps
- Added `has_valid_content` property - True if any content field set
- Added `content_fields` property - list of populated field names
- Added bidirectional Paper ↔ Pattern relationship
- Added 3 indexes: paper_id, status, (paper_id, status)

### Files Created

```
backend/app/models/pattern.py         # Pattern model + enum
backend/app/models/paper.py           # Added patterns relationship
backend/app/models/__init__.py        # Updated exports
backend/tests/test_models/test_pattern.py  # 25 tests
```

### Tests (25)

- Enum values (3)
- Model defaults and persistence (7)
- `has_valid_content` validation (6)
- `content_fields` property (6)
- Paper-Pattern relationship and cascade delete (3)

---

## Slice 3: Paper Pydantic Schemas

**PR:** #14

### What We Did

- Created `PaperMetadataInput` - user-provided upload metadata (all optional)
- Created `PaperMetadataExtracted` - Claude extraction results
  - confidence score (0.0-1.0, default 0.8)
  - year, one_sentence_summary fields
- Created `PaperResponse` - full paper for API responses
- Created `PaperListResponse` - paginated listing

### Files Created

```
backend/app/schemas/paper.py           # Paper schemas
backend/app/schemas/__init__.py        # Updated exports
backend/tests/test_schemas/__init__.py
backend/tests/test_schemas/test_paper_schemas.py  # 19 tests
```

### Tests (19)

- PaperMetadataInput validation (5)
- PaperMetadataExtracted with confidence bounds (7)
- PaperResponse required/optional fields (4)
- PaperListResponse pagination (3)

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Write from scratch vs copy | Cleaner code, avoids SRAL artifacts, follows OSS specs |
| Claim/Evidence/Context fields | Generic schema applicable to any research domain |
| `has_valid_content` property | Model-level validation helper |
| `content_fields` property | Useful for API responses and embedding text prep |
| confidence 0.0-1.0 | Standard probability range for extraction confidence |
| datetime.date import | Avoid name collision with `date` field name |

---

## Test Summary

| Slice | New Tests | Total |
|-------|-----------|-------|
| Slice 1 (Paper model) | 15 | 175 |
| Slice 2 (Pattern model) | 25 | 200 |
| Slice 3 (Paper schemas) | 19 | 219 |
| **Total Phase 3** | **59** | **219** |

---

## Open Questions / Next Steps

- [ ] Slice 4: Pattern Pydantic schemas (ExtractedPattern, PatternResponse, etc.)
- [ ] Slice 5: Alembic migration for initial schema
- [ ] Consider adding `PaperUploadResponse` schema (depends on Pattern schemas)
