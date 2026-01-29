# Backend (FastAPI)

Backend API for the SusBonk dashboard and services.

## Run (Docker Compose)

From repo root:

```bash
cp .env.example .env
# edit .env and replace CHANGE_ME_* values

docker compose up -d postgres redis backend
```

Health check (if available in your current backend build):

```bash
curl -f http://localhost:8000/health || true
```

## Local Development

This service uses `uv` (`pyproject.toml` + `uv.lock`).

```bash
uv sync --all-groups
uv run main.py
```
