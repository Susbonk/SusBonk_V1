# SusBonk TODO Tracker

## High Priority

### Backend API (Python)
- [ ] Implement FastAPI server with core endpoints
- [ ] User authentication and session management
- [ ] Settings CRUD endpoints (whitelist, custom blocks, moderation toggles)
- [ ] Integration with PostgreSQL for user data
- [ ] WebSocket support for real-time dashboard updates

### Telegram Bot Integration
- [ ] Bot setup and webhook configuration
- [ ] Message handler for spam detection
- [ ] User action commands (ban, delete, whitelist)
- [ ] Group admin verification
- [ ] Rate limiting and flood protection

### Frontend-Backend Integration
- [ ] Connect dashboard to backend API
- [ ] Real-time log streaming from OpenSearch
- [ ] Settings persistence and sync
- [ ] Authentication flow implementation
- [ ] Error handling and loading states

### AI Service
- [ ] Spam/scam detection model integration
- [ ] Message classification pipeline
- [ ] Model training and fine-tuning infrastructure
- [ ] Confidence scoring and thresholds

## Medium Priority

### Database Layer
- [ ] PostgreSQL schema implementation
- [ ] Migration system setup
- [ ] User settings and preferences tables
- [ ] Whitelist/blacklist storage
- [ ] Audit log tables

### Redis Integration
- [ ] Message queue implementation for bot events
- [ ] Session caching
- [ ] Rate limiting with Redis
- [ ] Real-time event pub/sub

### Monitoring & Observability
- [ ] Prometheus metrics export
- [ ] Grafana dashboards for system health
- [ ] Alert rules for critical failures
- [ ] Performance profiling and optimization

### Security
- [ ] JWT token implementation
- [ ] API key management system
- [ ] Input validation and sanitization
- [ ] Rate limiting on all endpoints
- [ ] CORS configuration

## Low Priority

### UI/UX Enhancements
- [ ] Dark mode toggle
- [ ] Mobile responsive improvements
- [ ] Keyboard shortcuts
- [ ] Export logs functionality
- [ ] Bulk whitelist import/export

### Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide for group moderators
- [ ] Deployment guide for self-hosting
- [ ] Contributing guidelines
- [ ] Architecture diagrams

### Testing
- [ ] Frontend unit tests (Vitest)
- [ ] Backend unit tests (pytest)
- [ ] Integration tests for API endpoints
- [ ] E2E tests (Playwright)
- [ ] Load testing for high-traffic scenarios

### DevOps
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated Docker builds
- [ ] Staging environment setup
- [ ] Production deployment scripts
- [ ] Backup and restore procedures

## Known Gaps

### Authentication & Authorization
- [ ] Refresh token rotation mechanism
- [ ] OAuth integration for social login
- [ ] Multi-factor authentication support
- [ ] Session timeout and renewal
- [ ] Role-based access control (RBAC)

### UI Features
- [ ] Deleted messages history view
- [ ] Message preview in logs
- [ ] Prompt linking UI for custom responses
- [ ] Batch operations on logs
- [ ] Advanced search and filtering

### Data Management
- [ ] Log retention policy configuration UI
- [ ] Data export compliance (GDPR)
- [ ] Automatic data purging
- [ ] Backup verification system

### Bot Features
- [ ] Multi-language support
- [ ] Custom bot responses/prompts
- [ ] Scheduled moderation rules
- [ ] User reputation system
- [ ] Appeal/unban workflow

### Infrastructure
- [ ] Horizontal scaling strategy
- [ ] Database replication and failover
- [ ] CDN for static assets
- [ ] DDoS protection
- [ ] Cost optimization

## Completed

### Log Platform
- [x] Unified Rust workspace with shared types
- [x] HTTP log ingestion service (ingestd)
- [x] Spam detection and monitoring (alertd)
- [x] OpenSearch integration with ECS schema
- [x] Daily index rotation with 7-day retention
- [x] Docker Compose orchestration
- [x] Multi-stage Docker builds

### Frontend
- [x] Svelte dashboard with tabbed interface
- [x] Persistent bottom navigation
- [x] Whitelist management modal
- [x] Collapsible moderation sections
- [x] UI design system and components
- [x] TypeScript integration

### Infrastructure
- [x] OpenSearch cluster setup
- [x] OpenSearch Dashboards configuration
- [x] Index templates and ISM policies
- [x] Health check system
- [x] Redis Streams prototype

---

**Last Updated:** 2026-01-29
