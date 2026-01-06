# Phase 4: Extraction Service Implementation

## Overview

Implemented pattern extraction services using the Claim/Evidence/Context schema with a 3-pass evidence-anchored pipeline.

**Goal**: Extract structured patterns from papers using Claude, prepare embeddings, and support the ingestion workflow.

**Dependencies**: Phase 3 complete (models, schemas, migrations exist)

---

## Architecture: 3-Pass Evidence-Anchored Extraction

### Pipeline Design

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Pass 1        │     │   Pass 2        │     │   Pass 3        │
│   Evidence      │ ──> │   Pattern       │ ──> │   Verification  │
│   Inventory     │     │   Extraction    │     │                 │
│   (Haiku)       │     │   (Sonnet)      │     │   (Haiku)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Pass 1: Evidence Inventory** (Haiku, temp=0.2)
   - Extracts 12-25 concrete evidence items with unique [E#] IDs
   - Each item: quote, location, type, importance
   - Grounds all subsequent analysis in verifiable source material

2. **Pass 2: Pattern Extraction** (Sonnet, temp=0.2)
   - Extracts 3-8 patterns with Claim/Evidence/Context
   - Every assertion must cite evidence: `[E#]` format
   - Claim/Evidence/Context must be DIFFERENT content (not repeated)

3. **Pass 3: Verification** (Haiku, temp=0.1)
   - Validates citation validity and accuracy
   - Checks coverage of evidence used
   - Returns verification result (pass/warn/fail)

### Multi-Model Strategy

| Pass | Model | Temperature | Purpose |
|------|-------|-------------|---------|
| 1 | Haiku 3.5 | 0.2 | Evidence extraction (cost-efficient) |
| 2 | Sonnet 4 | 0.2 | Pattern extraction (quality-critical) |
| 3 | Haiku 3.5 | 0.1 | Verification (consistency) |

---

## Slices Completed

### Slice 1: MetadataExtractor Service

**Files Created:**
- `backend/app/services/metadata_extractor.py`
- `backend/app/services/prompts/metadata.py`
- `backend/tests/test_services/test_metadata_extractor.py`

**Features:**
- Extract paper metadata (title, authors, year, type, summary)
- Merge PDF hints with LLM extraction
- User overrides take precedence
- Confidence scoring

**Tests:** 16

### Slice 2: Evidence Inventory Prompt (Pass 1)

**Files Created:**
- `backend/app/services/prompts/evidence_inventory.py`
- `backend/tests/test_services/test_prompts/test_evidence_inventory.py`

**Features:**
- Evidence types: finding, definition, mechanism, limitation, comparison, claim
- Importance levels: high, medium, low
- Paper type classification: empirical, theoretical, system, survey, position
- Defensive parsing for malformed LLM output

**Tests:** 24

### Slice 3: Pattern Extraction Prompt (Pass 2)

**Files Created:**
- `backend/app/services/prompts/extraction.py`
- `backend/tests/test_services/test_prompts/test_extraction.py`

**Features:**
- ExtractedPatternRaw model with Claim/Evidence/Context fields
- PatternConfidence enum (high/medium/low)
- [E#] citation requirements and parsing
- Evidence ID extraction helper

**Tests:** 43

### Slice 4: Verification Prompt (Pass 3)

**Files Created:**
- `backend/app/services/prompts/verification.py`
- `backend/tests/test_services/test_prompts/test_verification.py`

**Features:**
- VerificationStatus enum (pass/warn/fail)
- CitationIssue and AccuracyConcern models
- `compute_verification_status()` for consistent status rules
- Override LLM status when computed status differs

**Tests:** 37

### Slice 5: PatternExtractor Service

**Files Created:**
- `backend/app/services/pattern_extractor.py`
- `backend/tests/test_services/test_pattern_extractor.py`

**Features:**
- Orchestrates 3-pass pipeline
- Lazy client initialization
- Builds user-facing warnings from verification
- Overrides LLM status with computed status

**Tests:** 15

### Slice 6: EmbeddingService

**Files Created:**
- `backend/app/services/embedding_service.py`
- `backend/tests/test_services/test_embedding_service.py`

**Features:**
- OpenAI text-embedding-3-small (1536 dimensions)
- `prepare_embedding_text()` combines name/claim/evidence/context
- Batch processing (20 patterns) with individual fallback
- Exponential backoff retry for rate limits

**Tests:** 30

### Slice 7: Synthesis Prompt

**Files Created:**
- `backend/app/services/prompts/synthesis.py`
- `backend/tests/test_services/test_prompts/test_synthesis.py`

**Features:**
- PatternContext and SynthesisResult models
- Pattern context builder with markdown sanitization
- Conversation history formatting
- [P:id] citation format for synthesis

**Tests:** 35

### Slice 8: Service Integration & Documentation

**Files Modified:**
- `backend/app/services/__init__.py` - Added exports
- `backend/app/services/prompts/__init__.py` - Added exports
- `backend/CLAUDE.md` - Added service documentation
- `docs/devlog/phase-4-extraction.md` - This file
- `PLAN.md` - Updated progress

---

## Test Summary

| Slice | Tests Added |
|-------|-------------|
| Slice 1 (MetadataExtractor) | 16 |
| Slice 2 (Evidence Inventory) | 24 |
| Slice 3 (Extraction) | 43 |
| Slice 4 (Verification) | 37 |
| Slice 5 (PatternExtractor) | 15 |
| Slice 6 (EmbeddingService) | 30 |
| Slice 7 (Synthesis) | 35 |
| **Total Phase 4** | **200** |

---

## Key Decisions

1. **3-Pass Pipeline**: Chose evidence-anchored approach over single-pass for better quality and reproducibility

2. **Multi-Model Strategy**: Haiku for Pass 1/3 (cost-efficient), Sonnet for Pass 2 (quality-critical)

3. **Lazy Client Initialization**: PatternExtractor creates LLM clients on first use, not at construction

4. **Status Override**: Computed verification status overrides LLM-provided status for consistency

5. **Batch Embeddings**: Process 20 patterns per batch with fallback to individual on error

6. **Chunking Deferred**: Paper chunking for long documents deferred to Phase 5 (Workflows)

---

## Session Log

| Date | Engineer | What Changed |
|------|----------|--------------|
| 2026-01-05 | Claude | Slices 1-2: MetadataExtractor, Evidence Inventory |
| 2026-01-05 | Claude | Slices 3-4: Extraction, Verification prompts |
| 2026-01-06 | Claude | Slices 5-6: PatternExtractor, EmbeddingService |
| 2026-01-06 | Claude | Slices 7-8: Synthesis prompt, Documentation |

---

## Next Steps (Phase 5: Workflows)

1. Implement paper ingestion workflow orchestration
2. Add paper chunking for long documents
3. Connect extraction pipeline to database persistence
4. Build query workflow with synthesis
