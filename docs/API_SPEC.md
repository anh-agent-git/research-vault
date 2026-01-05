# API Specification

> **Document Type:** REST API endpoint contracts
> **Status:** Specification (pre-implementation)

---

## Overview

Research Vault exposes a REST API for paper ingestion, pattern management, and natural language querying. All endpoints are prefixed with `/api`.

**Base URL:** `http://localhost:8000/api`

---

## Authentication

No authentication required (single-user local deployment).

---

## Common Response Formats

### Success Response

```json
{
  "data": { ... }
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request body |
| `NOT_FOUND` | 404 | Resource not found |
| `EXTRACTION_FAILED` | 500 | LLM extraction error |
| `EMBEDDING_FAILED` | 500 | Embedding generation error |
| `SESSION_NOT_FOUND` | 404 | Query session expired or invalid |
| `SESSION_LIMIT_REACHED` | 503 | Max concurrent sessions |

---

## Health Check

### GET /health

Check system health and dependencies.

**Response:**

```json
{
  "status": "ok | degraded | error",
  "database": "ok | error",
  "qdrant": "ok | error",
  "sessions": 5,
  "tracing": "enabled | disabled"
}
```

| Status | Meaning |
|--------|---------|
| `ok` | All systems operational |
| `degraded` | Some systems unavailable |
| `error` | Critical failure |

---

## Papers

### POST /api/papers

Upload a paper for pattern extraction.

**Content-Type:** `multipart/form-data`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | No* | PDF file (max 10MB, 50 pages) |
| `text` | String | No* | Plain text content |
| `title` | String | No | Override extracted title |
| `authors` | String | No | Comma-separated author names |
| `source` | String | No | URL or source reference |
| `published_date` | String | No | ISO date (YYYY-MM-DD) |
| `type` | String | No | Paper type (default: `research_paper`) |

*Either `file` or `text` is required.

**Response:** `201 Created`

```json
{
  "paper_id": "uuid",
  "metadata": {
    "title": "Extracted or provided title",
    "authors": ["Author 1", "Author 2"],
    "source": "https://...",
    "published_date": "2024-01-15",
    "type": "research_paper"
  },
  "patterns": [
    {
      "temp_id": "temp-uuid",
      "name": "Pattern name (3-6 words)",
      "claim": "Main assertion...",
      "evidence": "Supporting quote...",
      "context": "Implications...",
      "tags": ["methodology", "finding"]
    }
  ],
  "extraction_warnings": ["Warning message if any"]
}
```

**Errors:**

| Code | Condition |
|------|-----------|
| `VALIDATION_ERROR` | No file or text provided |
| `VALIDATION_ERROR` | File too large (>10MB) |
| `VALIDATION_ERROR` | Invalid file type |
| `EXTRACTION_FAILED` | LLM extraction error |

---

### GET /api/papers

List papers with optional filters.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | String | - | Filter by status |
| `type` | String | - | Filter by paper type |
| `search` | String | - | Search in title |
| `limit` | Integer | 50 | Max results (1-100) |
| `offset` | Integer | 0 | Pagination offset |

**Response:** `200 OK`

```json
{
  "papers": [
    {
      "id": "uuid",
      "title": "Paper Title",
      "authors": ["Author 1"],
      "published_date": "2024-01-15",
      "type": "research_paper",
      "status": "active",
      "pattern_count": 5,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

---

### GET /api/papers/{paper_id}

Get a single paper with full details.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "date": "2024-01-15",
  "source": "https://...",
  "published_date": "2024-01-15",
  "type": "research_paper",
  "status": "active",
  "pattern_count": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**

| Code | Condition |
|------|-----------|
| `NOT_FOUND` | Paper does not exist |

---

### DELETE /api/papers/{paper_id}

Delete a paper and all associated patterns.

**Response:** `204 No Content`

**Side Effects:**
- Removes all patterns from database
- Removes all embeddings from Qdrant

**Errors:**

| Code | Condition |
|------|-----------|
| `NOT_FOUND` | Paper does not exist |

---

### POST /api/papers/{paper_id}/patterns

Submit pattern review decisions (approve/reject).

**Request Body:**

```json
{
  "decisions": [
    {
      "temp_id": "temp-uuid-from-upload",
      "approved": true
    },
    {
      "temp_id": "temp-uuid-2",
      "approved": false
    }
  ]
}
```

**Response:** `200 OK`

```json
{
  "saved_count": 3,
  "rejected_count": 2,
  "patterns": [
    {
      "id": "uuid",
      "name": "Pattern name",
      "claim": "...",
      "evidence": "...",
      "context": "...",
      "tags": ["tag1"],
      "status": "approved"
    }
  ]
}
```

**Side Effects:**
- Approved patterns are embedded and stored in Qdrant
- Paper status changes to `active` if any patterns approved
- Rejected patterns are discarded

**Errors:**

| Code | Condition |
|------|-----------|
| `NOT_FOUND` | Paper does not exist |
| `VALIDATION_ERROR` | Paper not in `ready_for_review` status |
| `EMBEDDING_FAILED` | Embedding generation error |

---

### GET /api/papers/{paper_id}/patterns

Get all patterns for a paper.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | String | - | Filter by status (approved, rejected) |

**Response:** `200 OK`

```json
{
  "patterns": [
    {
      "id": "uuid",
      "name": "Pattern name",
      "claim": "Main assertion...",
      "evidence": "Supporting quote...",
      "context": "Implications...",
      "tags": ["methodology"],
      "status": "approved",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## Patterns

### PUT /api/patterns/{pattern_id}

Update an existing pattern.

**Request Body:**

```json
{
  "name": "Updated name",
  "claim": "Updated claim...",
  "evidence": "Updated evidence...",
  "context": "Updated context...",
  "tags": ["updated", "tags"]
}
```

All fields are optional. Only provided fields are updated.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "name": "Updated name",
  "claim": "Updated claim...",
  "evidence": "Updated evidence...",
  "context": "Updated context...",
  "tags": ["updated", "tags"],
  "status": "approved",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Side Effects:**
- If claim, evidence, or context changed, pattern is re-embedded in Qdrant

**Errors:**

| Code | Condition |
|------|-----------|
| `NOT_FOUND` | Pattern does not exist |
| `VALIDATION_ERROR` | All content fields would be empty |
| `EMBEDDING_FAILED` | Re-embedding error |

---

### DELETE /api/patterns/{pattern_id}

Delete a single pattern.

**Response:** `204 No Content`

**Side Effects:**
- Removes embedding from Qdrant

**Errors:**

| Code | Condition |
|------|-----------|
| `NOT_FOUND` | Pattern does not exist |

---

## Query

### POST /api/query

Submit a natural language query.

**Request Body:**

```json
{
  "query": "What patterns exist about agent memory limitations?",
  "session_id": "uuid-optional",
  "filters": {
    "paper_type": ["research_paper", "blog_post"],
    "tags": ["methodology"],
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "exclude_archived": true
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | String | Yes | Natural language query (min 1 char) |
| `session_id` | UUID | No | Continue existing session |
| `filters` | Object | No | Scope the query |

**Filters:**

| Field | Type | Description |
|-------|------|-------------|
| `paper_type` | String[] | Filter by paper types (OR) |
| `tags` | String[] | Filter by pattern tags (ANY match) |
| `date_from` | Date | Papers published on or after |
| `date_to` | Date | Papers published on or before |
| `exclude_archived` | Boolean | Exclude archived papers (default: true) |

**Response:** `200 OK`

```json
{
  "session_id": "uuid",
  "response": "Based on the patterns in your library...\n\n- **Pattern Name** (Paper Title): Claim text with evidence.\n\n...",
  "sources": [
    {
      "pattern_id": "uuid",
      "paper_id": "uuid",
      "paper_title": "Paper Title",
      "pattern_name": "Pattern Name",
      "relevance_score": 0.92
    }
  ]
}
```

**Side Effects:**
- Creates new session if `session_id` not provided
- Updates session with query and response

**Errors:**

| Code | Condition |
|------|-----------|
| `VALIDATION_ERROR` | Empty query |
| `SESSION_NOT_FOUND` | Invalid or expired session_id |
| `SESSION_LIMIT_REACHED` | Max concurrent sessions (1000) |

---

### POST /api/query/followup

Submit a follow-up query in an existing session.

**Request Body:**

```json
{
  "query": "Tell me more about the first one",
  "session_id": "uuid-required"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | String | Yes | Follow-up question |
| `session_id` | UUID | Yes | Existing session ID |

**Response:** Same as `POST /api/query`

**Behavior:**
- Uses conversation history for context
- Maintains same filters as original query

**Errors:**

| Code | Condition |
|------|-----------|
| `VALIDATION_ERROR` | Empty query or missing session_id |
| `SESSION_NOT_FOUND` | Session expired or invalid |

---

## Session Behavior

### Session Lifecycle

1. **Creation:** First query without `session_id` creates a new session
2. **Continuation:** Subsequent queries with `session_id` continue the session
3. **Expiration:** Sessions expire after 30 minutes of inactivity
4. **Cleanup:** Expired sessions are garbage collected periodically

### Session Limits

| Limit | Value |
|-------|-------|
| Max concurrent sessions | 1000 |
| Session TTL | 30 minutes |
| Max turns per session | 100 |
| Max content per turn | 100KB |

---

## Rate Limits

No rate limits for local deployment. Future cloud deployment may add:

| Endpoint | Limit |
|----------|-------|
| `POST /api/papers` | 10/minute |
| `POST /api/query` | 30/minute |

---

## Pagination

List endpoints support offset-based pagination:

```
GET /api/papers?limit=20&offset=40
```

Response includes pagination metadata:

```json
{
  "papers": [...],
  "total": 100,
  "limit": 20,
  "offset": 40
}
```

---

## OpenAPI

Interactive API documentation available at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`
