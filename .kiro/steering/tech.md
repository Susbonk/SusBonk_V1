# Technical Architecture

## Technology Stack
**Frontend**: Svelte with TypeScript - Modern, reactive framework for fast, lightweight web interfaces
**Backend**: Unified Rust workspace - `log-platform` with shared types and multiple service binaries
**Message Processing**: 
- `ingestd` (Rust) - HTTP log ingestion service with bulk indexing to OpenSearch
- `alertd` (Rust) - Spam detection engine + infrastructure monitoring + email alerts
**Database**: PostgreSQL - User settings, prompts, chat configurations (planned)
**Logging & Analytics**: OpenSearch + Dashboards - ECS-compliant logs with daily indices and 7-day retention
**Message Queue**: Redis Streams with Consumer Groups - Producer/Worker pattern (prototyped)
**Deployment**: Docker Compose with multi-stage builds, cloud hosting (AWS/DigitalOcean planned)

## Architecture Overview
**Multi-Service Architecture**:
- **Svelte Frontend**: Tabbed dashboard interface with Dashboard, Logs, and Settings views (in progress)
- **log-platform (Rust Workspace)**: Unified Cargo workspace with shared types
  - **ingestd**: HTTP server on port 8080, `/ingest` endpoint, bulk indexing to OpenSearch
  - **alertd**: Spam detection + monitoring, writes logs via ingestd HTTP API
- **OpenSearch Stack**: 
  - OpenSearch (os01) on port 9200 with cluster health checks
  - Dashboards (osd01) on port 5601 for log visualization
  - Daily index pattern: `logs-{service}-{YYYY.MM.DD}`
  - ISM policy for automatic 7-day retention
- **Telegram Bot Service**: Python-based bot for group integration (planned)
- **Database Layer**: PostgreSQL for user data (planned); OpenSearch for logs and alerts (active)
- **Message Queue**: Redis Streams with Consumer Groups (prototyped in redis-example/)

## Implementation Details
**Log Platform Architecture**:
- **Shared Library** (`lib.rs`): Common types (LogEvent, Service, LogMeta, Trace)
- **ECS-Compliant Schema**: @timestamp, nested service.name, log.level fields
- **Index Strategy**: Service-specific daily indices with unified "logs" alias
- **Service Dependencies**: alertd → log-ingest health → os01 health
- **Healthchecks**: Curl-based checks prevent startup failures
- **Docker Images**: Multi-stage builds (157-168MB final size)

## Development Environment
**Required Tools**:
- Node.js 18+ and npm/pnpm for Svelte development
- Python 3.9+ with pip and virtual environments
- Rust 1.70+ with Cargo for performance components
- PostgreSQL 14+ for local database development
- Redis 6+ for message queue and caching
- Docker and Docker Compose for containerization

## Code Standards
**Svelte**: Standard Svelte formatting with Prettier, TypeScript for type safety
**Python**: PEP 8 style guide, Black formatter, type hints with mypy
**Rust**: Standard rustfmt formatting, Clippy linting, comprehensive error handling
**API Design**: RESTful conventions, OpenAPI/Swagger documentation
**Git**: Conventional commits, feature branch workflow

## Testing Strategy
**Frontend**: Vitest for unit tests, Playwright for E2E testing
**Python**: pytest for unit/integration tests, FastAPI test client
**Rust**: Built-in cargo test framework, property-based testing with proptest
**Integration**: Docker Compose test environments
**Coverage**: Minimum 80% code coverage across all services

## Deployment Process
**CI/CD Pipeline**:
- GitHub Actions for automated testing and building
- Docker multi-stage builds for optimized containers
- Staging environment for pre-production testing
- Blue-green deployment for zero-downtime updates
- Health checks and rollback capabilities

## Performance Requirements
**Response Time**: Dashboard loads in <2 seconds, API responses <500ms
**Throughput**: Handle 1000+ messages per second per group
**Scalability**: Horizontal scaling for high-traffic groups
**Availability**: 99.9% uptime with automated failover

## Security Considerations
**Authentication**: JWT tokens for dashboard access, API key management
**Data Protection**: Encryption at rest and in transit, GDPR compliance
**Bot Security**: Secure webhook handling, rate limiting, input validation
**Privacy**: Minimal data collection, automatic data purging policies
