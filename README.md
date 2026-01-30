# SusBonk

Automated spam and scam protection for Telegram groups with a user-friendly web dashboard.

## Demo Video

YouTube: https://youtu.be/pR2z8mwOCio

## System Overview

SusBonk provides AI-powered spam detection with centralized logging, real-time monitoring, and an intuitive control interface for non-technical group moderators.

## Services

| Service | Purpose | Tech |
|---------|---------|------|
| **frontend** | Web dashboard UI (Dashboard/Logs/Settings tabs) | Svelte + TypeScript |
| **admin** | Django admin interface for database management | Django + PostgreSQL |
| **backend** | REST API for dashboard, user management | Python + FastAPI |
| **telegram-bot** | Telegram group integration and message handling | Rust (teloxide) |
| **ai-service** | Spam/scam detection worker (Redis Streams) | Rust |
| **log-platform** | Unified logging platform (ingestd + alertd) | Rust workspace |
| **log-platform/ingestd** | HTTP log ingestion service with bulk indexing | Rust (port 8080) |
| **log-platform/alertd** | Spam detection + infrastructure monitoring | Rust |
| **OpenSearch** | Log storage and analytics (ECS-compliant) | OpenSearch 2.x |
| **OpenSearch Dashboards** | Log visualization and queries | OpenSearch Dashboards |
| **PostgreSQL** | User settings, configurations | PostgreSQL 14+ |
| **Redis** | Message queue, caching | Redis 7+ |

## Quick Start

### Docker Compose (Recommended)

```bash
# Create local env file
cp .env.example .env
# edit .env and replace CHANGE_ME_* values

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Judge Quickstart

```bash
cp .env.example .env
# edit .env and replace CHANGE_ME_* values

docker compose up -d

# Quick health checks
curl -f http://localhost:8000/health || true
curl -f http://localhost:8080/health || true
```

### Non-Compose Development

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

**Log Platform (Rust):**
```bash
cd log-platform

# Build both services
cargo build --release

# Run ingestd
cargo run --bin ingestd

# Run alertd (separate terminal)
cargo run --bin alertd
```

**OpenSearch (manual):**
```bash
# Requires OpenSearch 2.x installed locally
# Run initialization script
cd log-platform/init
./init.sh
```

## Access Points

| Service | URL | Port |
|---------|-----|------|
| Frontend Dashboard | http://localhost:5173 | 5173 |
| Django Admin | http://localhost:8090/admin | 8090 |
| Backend API | http://localhost:8000 | 8000 |
| AI Service | http://localhost:8001 | 8001 |
| Log Ingestion API | http://localhost:8080 | 8080 |
| OpenSearch API | http://localhost:9200 | 9200 |
| OpenSearch Dashboards | http://localhost:5601 | 5601 |
| PostgreSQL | localhost:5432 | 5432 |
| Redis | localhost:6379 | 6379 |

**Local Credentials (Dev Only):**
- Credentials and passwords come from your `.env` file (see `.env.example` and `docs/SECURITY_SETUP.md`).
- Do not reuse local dev passwords for production.

## Production Notes

**Environment Variables:**
- `OPENSEARCH_URL` - OpenSearch endpoint
- `OPENSEARCH_USER` - OpenSearch username
- `OPENSEARCH_PASSWORD` - OpenSearch password
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `TELEGRAM_BOT_TOKEN` - Bot API token

**Secrets Management:**
- Store credentials in `.env` files (never commit)
- Use secrets manager in cloud deployments
- Rotate API keys and tokens regularly

**Persistent Volumes:**
- `opensearch-data` - Log indices and cluster state
- `postgres-data` - User data and configurations
- `redis-data` - Queue persistence

**Health Checks:**
- All services include Docker healthchecks
- Startup dependencies enforced via `depends_on`
- Monitor via OpenSearch Dashboards or `/health` endpoints

## Documentation

- [Product Overview](.kiro/steering/product.md)
- [Technical Architecture](.kiro/steering/tech.md)
- [Project Structure](.kiro/steering/structure.md)
- [TODO Tracker](TODO.md) - Outstanding work and known gaps
