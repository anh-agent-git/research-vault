# Contributing to Research Vault

Thank you for your interest in contributing to Research Vault! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a feature branch from `main`

## Development Setup

### Backend

```bash
cd backend
uv sync                          # Install dependencies
uv run alembic upgrade head      # Run migrations
uv run uvicorn app.main:app --reload  # Start server
```

### Frontend

```bash
cd frontend
npm install                      # Install dependencies
npm run dev                      # Start dev server
```

### Docker (Full Stack)

```bash
docker compose up                # Start all services
```

### Pre-commit Hooks

Install pre-commit hooks to catch issues before committing:

```bash
pip install pre-commit           # Install pre-commit
pre-commit install               # Set up git hooks
pre-commit run --all-files       # Run on all files (optional)
```

This will automatically run:
- **Secret detection** (detect-secrets, gitleaks) - prevents accidental credential commits
- **Python linting** (ruff) - catches code issues
- **File checks** - trailing whitespace, large files, merge conflicts

## Code Standards

### Python (Backend)

- **Formatter:** ruff format
- **Linter:** ruff check
- **Type hints:** Required for all functions
- **Tests:** pytest with mocked external services

```bash
uv run ruff check .              # Lint
uv run ruff format .             # Format
uv run pytest                    # Test
```

### TypeScript (Frontend)

- **Linter:** ESLint
- **Formatter:** Prettier
- **Types:** Strict TypeScript

```bash
npm run lint                     # Lint
npm run build                    # Type check + build
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests for new functionality
   - Ensure all tests pass
   - Follow code standards

3. **Commit with clear messages**
   ```
   Add user authentication endpoint

   - Implement JWT token generation
   - Add login/logout routes
   - Include unit tests
   ```

4. **Push and create PR**
   - Fill out the PR template
   - Link related issues
   - Request review

5. **Address feedback**
   - Respond to review comments
   - Push additional commits as needed

## Testing

All contributions must include tests:

- **Unit tests** for new services/utilities
- **Integration tests** for API endpoints
- **Update existing tests** if behavior changes

### Running Tests

```bash
# Run all backend tests
cd backend
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run unit tests only (faster)
uv run pytest tests/ --ignore=tests/test_integration

# Run integration tests only
uv run pytest tests/test_integration/

# Run frontend tests
cd frontend
npm test
```

### Integration Tests

Integration tests in `backend/tests/test_integration/` test the full workflow with mocked external services (LLM, embeddings, Qdrant). They verify:

- **Full pipeline:** Upload → Extract → Review → Query
- **Error handling:** Invalid inputs, service failures
- **Partial success:** System continues when non-critical components fail

When adding new features, include integration tests that verify end-to-end behavior.

## Security

### Before Committing

Run the security check script to catch potential issues:

```bash
bash scripts/security_check.sh
```

This checks for:
- Hardcoded API keys
- Personal file paths
- Tracked .env files
- SRAL migration artifacts
- Debug logging of secrets

### Security Guidelines

1. **Never commit secrets**
   - Use environment variables for API keys
   - Use `.env.example` with placeholder values
   - Pre-commit hooks will catch most issues

2. **No personal paths**
   - Don't hardcode `/Users/username/` or `/home/username/`
   - Use relative paths or environment variables

3. **Validate inputs**
   - Sanitize user-provided data
   - Use Pydantic schemas for validation
   - Limit file upload sizes

4. **Report vulnerabilities**
   - Email security issues privately
   - Don't open public issues for vulnerabilities

## Issue Guidelines

### Bug Reports

- Use the bug report template
- Include steps to reproduce
- Provide environment details

### Feature Requests

- Use the feature request template
- Explain the problem being solved
- Consider alternatives

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Open an issue with the `question` label or start a discussion.
