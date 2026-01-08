# Technical Architecture

## Technology Stack
**Frontend**: Svelte with TypeScript - Modern, reactive framework for fast, lightweight web interfaces
**Backend**: Python API Server - Dashboard API, user management, settings
**Message Processing**: Rust services - `ingestd` for high-speed log ingestion, `alertd` for spam detection + infrastructure monitoring
**Database**: PostgreSQL - User settings, prompts, chat configurations, user state
**Logging & Analytics**: OpenSearch - Message logs, alerts, and search analytics
**Message Queue**: Redis Streams with Consumer Groups - Producer/Worker pattern for message processing
**Deployment**: Docker containers with cloud hosting (AWS/DigitalOcean)

## Architecture Overview
**Multi-Service Architecture**:
- **Svelte Frontend**: Tabbed dashboard interface with Dashboard, Logs, and Settings views
- **Python API Server**: REST API for frontend, user management, settings
- **ingestd (Rust)**: High-speed message log ingestion service
- **alertd (Rust)**: Spam detection engine + infrastructure monitoring + email alerts
- **Telegram Bot Service**: Python-based bot for group integration
- **Database Layer**: PostgreSQL for user data, prompts, chat settings; OpenSearch for logs and alerts
- **Message Queue**: Redis Streams with Consumer Groups for Producer/Worker pattern

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
