# Operations Guide

This guide covers deployment, database management, monitoring, and troubleshooting for Research Vault.

## Table of Contents

- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Database Management](#database-management)
- [Vector Store Management](#vector-store-management)
- [Monitoring](#monitoring)
- [Logging](#logging)
- [Troubleshooting Runbook](#troubleshooting-runbook)
- [Backup and Recovery](#backup-and-recovery)

---

## Deployment

### Docker Compose (Recommended)

The simplest deployment method for single-server setups:

```bash
# Clone and configure
git clone https://github.com/aakashsharan/research-vault.git
cd research-vault
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v
```

**Services started:**
| Service | Port | Purpose |
|---------|------|---------|
| frontend | 3000 | Next.js web UI |
| backend | 8000 | FastAPI server |
| qdrant | 6333, 6334 | Vector database |

### Manual Deployment

For development or custom setups:

#### 1. Start Qdrant

```bash
# Using Docker
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:v1.16.2

# Or use Qdrant Cloud: https://cloud.qdrant.io/
```

#### 2. Deploy Backend

```bash
cd backend

# Install dependencies
uv sync --frozen

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
uv run alembic upgrade head

# Start with uvicorn (development)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start with gunicorn (production)
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 3. Deploy Frontend

```bash
cd frontend

# Install dependencies
npm ci

# Build for production
NEXT_PUBLIC_API_URL=http://your-backend:8000 npm run build

# Start production server
npm start
```

### Production Considerations

| Aspect | Recommendation |
|--------|----------------|
| Reverse proxy | Use nginx or Caddy for TLS termination |
| Process manager | Use systemd or Docker for auto-restart |
| Database | Consider PostgreSQL for production |
| Qdrant | Use Qdrant Cloud or dedicated instance |
| Secrets | Use environment variables or secret manager |

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key for extraction/synthesis | `sk-ant-...` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | `sk-proj-...` |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/research.db` | SQLAlchemy connection string |

**PostgreSQL example:**
```env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@localhost:5432/research_vault
```

### Qdrant Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | `localhost` | Qdrant server hostname |
| `QDRANT_PORT` | `6333` | Qdrant HTTP port |

**Qdrant Cloud:**
```env
QDRANT_HOST=your-cluster.qdrant.io
QDRANT_PORT=6333
# Note: Qdrant Cloud requires API key in code changes
```

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Default Claude model |

### Ingestion Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_PDF_PAGES` | `100` | Maximum pages to extract from PDF |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload file size |
| `EXTRACTION_TIMEOUT_SECONDS` | `120` | Pattern extraction timeout |
| `EXTRACTION_MAX_RETRIES` | `3` | Retry count for failed extractions |

### Observability (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGCHAIN_TRACING_V2` | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | (empty) | LangSmith API key |
| `LANGCHAIN_PROJECT` | `research-vault` | LangSmith project name |

---

## Database Management

### Alembic Migrations

Research Vault uses Alembic for database schema migrations.

```bash
cd backend

# Check current migration state
uv run alembic current

# Apply all pending migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>

# View migration history
uv run alembic history

# Create new migration (after model changes)
uv run alembic revision --autogenerate -m "description"
```

### Database Schema

**Tables:**
| Table | Description |
|-------|-------------|
| `papers` | Research papers with metadata |
| `patterns` | Extracted patterns (claim/evidence/context) |
| `alembic_version` | Migration tracking |

**Key relationships:**
- `patterns.paper_id` → `papers.id` (cascade delete)

### SQLite Maintenance

```bash
# Check database integrity
sqlite3 data/research.db "PRAGMA integrity_check;"

# Vacuum to reclaim space
sqlite3 data/research.db "VACUUM;"

# Show table sizes
sqlite3 data/research.db ".tables"
sqlite3 data/research.db "SELECT COUNT(*) FROM papers;"
sqlite3 data/research.db "SELECT COUNT(*) FROM patterns;"
```

---

## Vector Store Management

### Qdrant Collections

Research Vault uses a single collection for pattern embeddings:

| Collection | Dimensions | Distance | Description |
|------------|------------|----------|-------------|
| `patterns` | 1536 | Cosine | Pattern embeddings |

### Qdrant Operations

```bash
# Check Qdrant health
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/patterns

# Get collection points count
curl http://localhost:6333/collections/patterns | jq '.result.points_count'
```

### Qdrant Dashboard

Access the Qdrant web UI at: http://localhost:6333/dashboard

Features:
- Browse collections and points
- Run test searches
- View cluster status

---

## Monitoring

### Health Endpoint

The backend exposes a health check at `GET /health`:

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "database": "ok",
  "qdrant": "ok",
  "sessions": 5,
  "tracing": "disabled"
}
```

**Status values:**
| Status | Meaning |
|--------|---------|
| `ok` | All systems operational |
| `degraded` | Database OK, Qdrant unavailable |
| `error` | Database unavailable |

### Metrics to Monitor

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Health status | `/health` | != "ok" |
| Response time | Reverse proxy logs | > 5s |
| Error rate | Application logs | > 1% |
| Disk usage | Host system | > 80% |
| Memory usage | Docker stats | > 80% |
| Qdrant points | Qdrant API | Unexpected drops |

### Uptime Monitoring

Recommended tools:
- **Simple:** UptimeRobot, Pingdom (free tiers available)
- **Self-hosted:** Uptime Kuma
- **Cloud:** AWS CloudWatch, GCP Monitoring

Configure to check:
1. `http://your-domain:8000/health` - Backend health
2. `http://your-domain:3000` - Frontend accessibility
3. `http://your-domain:6333/health` - Qdrant health

---

## Logging

### Backend Logs

FastAPI logs to stdout by default. In Docker:

```bash
# View backend logs
docker compose logs -f backend

# View last 100 lines
docker compose logs --tail=100 backend
```

**Log levels:**
- `INFO` - Normal operations
- `WARNING` - Recoverable issues
- `ERROR` - Failed operations

### Frontend Logs

Next.js logs to stdout:

```bash
docker compose logs -f frontend
```

### Qdrant Logs

```bash
docker compose logs -f qdrant
```

### Log Aggregation

For production, consider:
- **Loki + Grafana** - Open source, integrates with Docker
- **ELK Stack** - Elasticsearch, Logstash, Kibana
- **Cloud services** - CloudWatch Logs, GCP Logging

---

## Troubleshooting Runbook

### Backend Won't Start

**Symptom:** Container exits immediately or API unreachable

1. Check logs:
   ```bash
   docker compose logs backend
   ```

2. Verify environment variables:
   ```bash
   docker compose config | grep -A20 backend
   ```

3. Test database connection:
   ```bash
   docker compose exec backend uv run python -c "from app.db import engine; print('OK')"
   ```

4. Common causes:
   - Missing API keys
   - Invalid DATABASE_URL
   - Port already in use

### Qdrant Connection Failed

**Symptom:** Health shows `"qdrant": "error"`

1. Check Qdrant is running:
   ```bash
   docker compose ps qdrant
   curl http://localhost:6333/health
   ```

2. Check network connectivity:
   ```bash
   docker compose exec backend curl http://qdrant:6333/health
   ```

3. Verify QDRANT_HOST/PORT match docker-compose service name

### Pattern Extraction Fails

**Symptom:** Upload succeeds but no patterns extracted

1. Check extraction warnings in API response
2. Verify ANTHROPIC_API_KEY is valid:
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
   ```
3. Check backend logs for rate limiting or API errors
4. Ensure paper content is substantial (not just a few words)

### Query Returns No Results

**Symptom:** Query returns empty or low-confidence response

1. Verify patterns exist and are approved:
   ```bash
   curl http://localhost:8000/api/papers | jq '.papers[].pattern_count'
   ```

2. Check Qdrant has vectors:
   ```bash
   curl http://localhost:6333/collections/patterns | jq '.result.points_count'
   ```

3. Verify OPENAI_API_KEY for embeddings:
   - Check backend logs for embedding errors
   - Test key directly with OpenAI API

### Database Migration Errors

**Symptom:** `alembic upgrade head` fails

1. Check current state:
   ```bash
   uv run alembic current
   ```

2. If stuck, check alembic_version table:
   ```bash
   sqlite3 data/research.db "SELECT * FROM alembic_version;"
   ```

3. For fresh start (WARNING: loses data):
   ```bash
   rm data/research.db
   uv run alembic upgrade head
   ```

### High Memory Usage

**Symptom:** Containers using excessive memory

1. Check container stats:
   ```bash
   docker stats
   ```

2. Limit memory in docker-compose.yml:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 1G
   ```

3. For Qdrant, adjust storage settings or use Qdrant Cloud

---

## Backup and Recovery

### SQLite Backup

```bash
# Stop writes (optional but recommended)
docker compose stop backend

# Copy database file
cp backend/data/research.db backup/research-$(date +%Y%m%d).db

# Restart
docker compose start backend
```

### SQLite Restore

```bash
docker compose stop backend
cp backup/research-20240101.db backend/data/research.db
docker compose start backend
```

### Qdrant Backup

Qdrant stores data in the `qdrant-data` Docker volume.

```bash
# Create snapshot via API
curl -X POST http://localhost:6333/collections/patterns/snapshots

# List snapshots
curl http://localhost:6333/collections/patterns/snapshots

# Download snapshot
curl http://localhost:6333/collections/patterns/snapshots/<snapshot_name> -o patterns-backup.snapshot
```

### Full System Backup

```bash
#!/bin/bash
BACKUP_DIR="backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Stop services
docker compose stop

# Backup SQLite
cp backend/data/research.db $BACKUP_DIR/

# Backup Qdrant volume
docker run --rm -v qdrant-data:/data -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/qdrant-data.tar.gz /data

# Restart services
docker compose start

echo "Backup complete: $BACKUP_DIR"
```

### Disaster Recovery

1. **Data loss in SQLite only:**
   - Restore from backup
   - Patterns still in Qdrant, but IDs may mismatch
   - May need to re-upload affected papers

2. **Data loss in Qdrant only:**
   - Patterns exist in SQLite but not searchable
   - Re-approve patterns to regenerate embeddings
   - Or restore Qdrant snapshot

3. **Complete data loss:**
   - Restore both SQLite and Qdrant from backup
   - Ensure backups are from same point in time
