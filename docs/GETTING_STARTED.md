# Getting Started with Research Vault

This guide walks you through setting up Research Vault locally and using it to build your research knowledge base.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 20.x | Frontend runtime |
| Docker | 24.x+ | Container runtime (for Qdrant) |
| uv | Latest | Python package manager |

### Installing Prerequisites

**Python 3.12:**
```bash
# macOS (with Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update && sudo apt install python3.12

# Verify
python3.12 --version
```

**Node.js 20:**
```bash
# macOS (with Homebrew)
brew install node@20

# Using nvm (recommended)
nvm install 20
nvm use 20

# Verify
node --version  # Should show v20.x.x
```

**Docker:**
```bash
# macOS
brew install --cask docker

# Ubuntu
sudo apt install docker.io docker-compose-plugin

# Verify
docker --version
```

**uv (Python package manager):**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
```

## API Keys

Research Vault requires API keys for LLM and embeddings:

| Provider | Purpose | Get Key |
|----------|---------|---------|
| Anthropic | Claude for extraction & synthesis | https://console.anthropic.com/ |
| OpenAI | Embeddings (text-embedding-3-small) | https://platform.openai.com/ |

Optional for tracing:

| Provider | Purpose | Get Key |
|----------|---------|---------|
| LangSmith | Observability & debugging | https://smith.langchain.com/ |

## Quick Start with Docker Compose

The fastest way to run the full stack:

### 1. Clone the Repository

```bash
git clone https://github.com/aakashsharan/research-vault.git
cd research-vault
```

### 2. Create Environment File

```bash
# Copy the example and fill in your keys
cp .env.example .env
```

Edit `.env` with your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=research-vault
```

### 3. Start the Stack

```bash
docker compose up --build
```

This starts:
- **Frontend** at http://localhost:3000
- **Backend** at http://localhost:8000
- **Qdrant** at http://localhost:6333

### 4. Verify Setup

Open http://localhost:8000/health in your browser. You should see:
```json
{
  "status": "ok",
  "database": "ok",
  "qdrant": "ok",
  "sessions": 0,
  "tracing": "disabled"
}
```

## Manual Setup (Development)

For development, run services individually:

### 1. Start Qdrant

```bash
docker compose up qdrant
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Create environment file
cp .env.example .env  # Edit with your API keys

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at http://localhost:3000

## Your First Upload

### 1. Navigate to Upload

Open http://localhost:3000/upload

### 2. Upload a Paper

You have two options:

**Option A: Upload PDF**
- Click "Choose File" and select a research paper PDF
- Optionally provide metadata (title, authors)
- Click "Upload"

**Option B: Paste Text**
- Switch to the "Text" tab
- Paste the paper content
- Add metadata (title, authors, source URL)
- Select paper type (Research Paper, Blog Post, etc.)
- Click "Submit"

### 3. Review Extraction

After upload, you'll be redirected to the review page showing:
- Extracted paper metadata
- Extracted patterns with Claim/Evidence/Context

### 4. Approve Patterns

Review each pattern:
- **Approve**: Pattern is added to your knowledge base
- **Reject**: Pattern is discarded

Click "Submit Review" when done.

## Your First Query

### 1. Navigate to Query

Open http://localhost:3000/query

### 2. Ask a Question

Type a question about your research library:
```
What patterns exist about agent memory?
```

### 3. Review Response

The system will:
1. Search your approved patterns semantically
2. Synthesize an answer grounded in your patterns
3. Show citations like `[P:pattern-id]`
4. Suggest follow-up questions

### 4. Follow Up

Click a suggested question or type your own to continue the conversation. The system maintains context across turns.

## Common Issues & Solutions

### Backend won't start

**Error:** `ANTHROPIC_API_KEY not set`
```bash
# Ensure .env file exists and has valid keys
cat backend/.env

# Keys should start with:
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-proj-...
```

**Error:** `Connection refused to Qdrant`
```bash
# Ensure Qdrant is running
docker compose up qdrant

# Check Qdrant health
curl http://localhost:6333/health
```

### Frontend can't connect to backend

**Error:** Network error or CORS issues
```bash
# Ensure backend is running
curl http://localhost:8000/api/health

# Check frontend environment
cat frontend/.env.local
# Should contain: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### PDF upload fails

**Error:** "PDF parsing failed"
- Ensure the PDF is not password-protected
- Try a different PDF to rule out file corruption
- Check backend logs for detailed error

### Pattern extraction returns empty

**Possible causes:**
1. Paper content too short (needs substantial text)
2. API rate limiting (check backend logs)
3. Text not recognizable as research content

**Solutions:**
- Try with longer, more detailed content
- Wait and retry if rate limited
- Check extraction warnings in the response

### Database migration issues

```bash
cd backend

# Check current migration state
uv run alembic current

# Reset if needed (WARNING: deletes data)
rm -rf data/research.db
uv run alembic upgrade head
```

### Docker memory issues

If containers crash due to memory:
```bash
# Increase Docker memory allocation
# Docker Desktop → Settings → Resources → Memory: 4GB+

# Or run with limits
docker compose up --scale frontend=1 --scale backend=1
```

## Next Steps

- **Browse Library**: http://localhost:3000/library - View and manage papers
- **API Documentation**: http://localhost:8000/docs - FastAPI Swagger UI
- **Domain Model**: See `docs/DOMAIN_MODEL.md` for entity relationships
- **API Spec**: See `docs/API_SPEC.md` for endpoint details

## Quick Reference: All Commands

### One-Time Setup

```bash
# Clone repository
git clone https://github.com/aakashsharan/research-vault.git
cd research-vault

# For Docker Compose (recommended):
cp .env.example .env
# Edit .env with your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-proj-...

# For manual development (without Docker):
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### Starting Services

**Option A: Docker Compose (Recommended)**
```bash
# Start everything (first time - builds images)
docker compose up --build

# Start everything (subsequent runs)
docker compose up

# Start in background
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

**Option B: Manual Development Setup**
```bash
# Terminal 1: Qdrant
docker compose up qdrant

# Terminal 2: Backend
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

### Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Service status |
| Qdrant | http://localhost:6333 | Vector DB dashboard |

### Running Tests

```bash
# Backend tests (619 tests)
cd backend
uv run pytest                                    # All tests
uv run pytest -v                                 # Verbose
uv run pytest tests/test_api/                    # API tests only
uv run pytest tests/test_integration/            # Integration tests only
uv run pytest --cov=app --cov-report=html        # With coverage report

# Frontend tests (23 tests)
cd frontend
npm test                                         # Run tests
npm run test:watch                               # Watch mode
```

### Linting & Formatting

```bash
# Backend
cd backend
uv run ruff check .                              # Lint
uv run ruff check --fix .                        # Lint + auto-fix
uv run ruff format .                             # Format

# Frontend
cd frontend
npm run lint                                     # ESLint
npm run build                                    # Type check + build
```

### Database Operations

```bash
cd backend

# Apply migrations
uv run alembic upgrade head

# Check migration status
uv run alembic current

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Rollback one migration
uv run alembic downgrade -1

# Reset database (WARNING: deletes data)
rm -rf data/research.db
uv run alembic upgrade head
```

### Security Checks

```bash
# Run security scan
bash scripts/security_check.sh

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Useful curl Commands

```bash
# Health check
curl http://localhost:8000/health | jq

# List papers
curl http://localhost:8000/api/papers | jq

# Upload text content
curl -X POST http://localhost:8000/api/papers \
  -F "text=Your paper content here..." \
  -F "title=My Paper Title" \
  -F "type=research_paper" | jq

# Query the library
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What patterns exist about agent memory?"}' | jq
```

## Pre-Release Testing Checklist

Before releasing or sharing the app, verify these work:

### 1. Fresh Setup Test
```bash
# Clean slate
docker compose down -v
rm -rf backend/data/

# Start fresh
docker compose up --build
```

### 2. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok", "database": "ok", "qdrant": "ok", ...}
```

### 3. Upload Flow
- Navigate to http://localhost:3000/upload
- Upload a PDF or paste text
- Verify patterns are extracted
- Review page shows patterns with Claim/Evidence/Context

### 4. Review Flow
- Approve some patterns, reject others
- Click "Submit Review"
- Verify redirect to library

### 5. Library View
- Navigate to http://localhost:3000/library
- Verify paper appears with correct status
- Click paper to see patterns
- Test filters (status, type)

### 6. Query Flow
- Navigate to http://localhost:3000/query
- Ask a question about uploaded content
- Verify response includes citations [P:id]
- Test follow-up questions
- Verify session history persists

### 7. Test All Endpoints
```bash
# Run full test suite
cd backend && uv run pytest -v
# Expected: 619 passed

cd frontend && npm test
# Expected: 23 passed
```

## Getting Help

- **Issues**: https://github.com/aakashsharan/research-vault/issues
- **Discussions**: https://github.com/aakashsharan/research-vault/discussions
