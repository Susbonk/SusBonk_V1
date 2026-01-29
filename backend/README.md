# SusBonk FastAPI Backend

FastAPI-based REST API for the SusBonk anti-spam platform.

## Features

- Async PostgreSQL with SQLAlchemy
- JWT authentication
- Redis integration for caching
- OpenSearch log shipping
- Health check endpoint
- CORS configuration
- Pydantic validation

## Prerequisites

- Python 3.13 (specified in `.python-version`)
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL 14+
- Redis 6+

## Quick Start

### Local Development

```bash
# Install dependencies with uv (uses uv.lock for reproducible builds)
cd backend
uv sync

# Set environment variables (or use .env file)
export POSTGRES_DB=susbonk
export POSTGRES_USER=susbonk
export POSTGRES_PASSWORD=susbonk_dev
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export REDIS_URL=redis://localhost:6379
export JWT_SECRET=your-secret-key

# Start server
uv run uvicorn main:main_app --reload --host 0.0.0.0 --port 8000
```

### Dependency Management

This project uses `uv` for dependency management:
- `pyproject.toml`: Declares dependencies
- `uv.lock`: Locks exact versions for reproducibility
- `.python-version`: Pins Python version to 3.13

To update dependencies:
```bash
# Add new dependency
uv add <package>

# Update all dependencies
uv lock --upgrade

# Sync environment with lockfile
uv sync
```

### Docker Deployment

```bash
# From project root
docker-compose up -d backend

# Access API
curl http://localhost:8000/health
```

## API Endpoints

- `GET /health` - Health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `GET /chats` - List chats
- `POST /chats` - Create chat
- `GET /prompts` - List prompts
- And more...

## Configuration

Environment variables (see `.env.example`):
- `POSTGRES_*`: Database connection
- `REDIS_URL`: Redis connection
- `JWT_SECRET`: JWT signing key
- `ENVIRONMENT`: development/production
- `CORS_ORIGINS`: Allowed CORS origins
- `OS_INGEST_URL`: OpenSearch ingest endpoint

## Lockfile Policy

This project uses `uv.lock` for deterministic dependency resolution:
- **Committed to git**: Yes, `uv.lock` is version controlled
- **Updated when**: Dependencies change in `pyproject.toml`
- **Docker builds**: Use `uv sync --frozen` to ensure exact versions
- **CI/CD**: Always use lockfile for reproducible builds

## Development

See [Python Dependency Policy](../docs/python-dependency-policy.md) for detailed information on version management.
