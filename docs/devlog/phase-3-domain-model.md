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
| 2026-01-05 | Claude Opus 4.5 | Slice 4: Pattern Pydantic schemas (PR #15) |
| 2026-01-05 | Claude Opus 4.5 | Slice 5: Initial Alembic migration (PR #16) |
| 2026-01-05 | Claude Opus 4.5 | Slice 6: Code review fixes - whitespace & CHECK constraint (PR #17) |

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

## Slice 4: Pattern Pydantic Schemas

**PR:** #15

### What We Did

- Created `ExtractedPattern` - internal DTO with validation (at least one content field required)
- Created `ExtractedPatternResponse` - for upload responses with temp_id
- Created `PatternResponse` - full pattern for API responses
- Created `PatternUpdateRequest` - for PUT endpoints with field validation
- Created `PatternDecision` and `PatternReviewRequest` - for review workflow
- Created `PatternReviewResponse` - review submission response

### Files Created

```
backend/app/schemas/pattern.py           # Pattern schemas
backend/app/schemas/__init__.py          # Updated exports
backend/tests/test_schemas/test_pattern_schemas.py  # 40 tests
```

### Tests (40)

- ExtractedPattern validation and content_fields (16)
- ExtractedPatternResponse serialization (7)
- PatternResponse required/optional fields (7)
- PatternUpdateRequest field validation (5)
- PatternDecision/ReviewRequest/Response (5)

---

## Slice 5: Initial Alembic Migration

**PR:** #16

### What We Did

- Created initial Alembic migration for papers and patterns tables
- Papers table with all fields and composite index
- Patterns table with foreign key to papers (CASCADE delete)
- Three indexes on patterns: paper_id, status, (paper_id, status)

### Files Created

```
backend/alembic/versions/41bbec096be1_initial_schema_with_papers_and_patterns_.py
```

---

## Slice 6: Code Review Fixes

**PR:** #17

### What We Did

Based on code review feedback:
- Fixed `has_valid_content` to reject whitespace-only strings
- Fixed `content_fields` to exclude whitespace-only strings
- Added `ck_patterns_has_content` CHECK constraint to patterns table
- Created migration to add CHECK constraint to existing table

### Files Modified

```
backend/app/models/pattern.py            # Updated properties and added CHECK constraint
backend/alembic/versions/d80764b2a617_add_check_constraint_for_pattern_content.py
backend/tests/test_models/test_pattern.py  # 6 new tests
```

### Tests (6)

- Whitespace handling in has_valid_content (2)
- Whitespace handling in content_fields (2)
- CHECK constraint enforcement (2)

---

## Test Summary

| Slice | New Tests | Total |
|-------|-----------|-------|
| Slice 1 (Paper model) | 15 | 175 |
| Slice 2 (Pattern model) | 25 | 200 |
| Slice 3 (Paper schemas) | 19 | 219 |
| Slice 4 (Pattern schemas) | 40 | 259 |
| Slice 5 (Alembic migration) | 0 | 259 |
| Slice 6 (Code review fixes) | 6 | 265 |
| **Total Phase 3** | **105** | **265** |

---

## Phase 3 Complete

All domain model implementation tasks completed:
- [x] Paper model with enums
- [x] Pattern model with Claim/Evidence/Context schema
- [x] Paper Pydantic schemas
- [x] Pattern Pydantic schemas
- [x] Alembic migrations (initial + CHECK constraint)
- [x] 105 new tests added
