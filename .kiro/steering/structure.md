# Project Structure

## Directory Layout
```
SusBonk/
├── frontend/                 # Svelte web dashboard
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/  # Svelte UI components
│   │   │   │   ├── App.svelte           # Main app component
│   │   │   │   ├── Dashboard.svelte     # Tabbed dashboard (Dashboard/Logs/Settings)
│   │   │   │   ├── Onboarding.svelte   # Initial setup flow
│   │   │   │   ├── DashboardHeader.svelte # Header with controls
│   │   │   │   ├── ModerationToggle.svelte # Spam category toggles
│   │   │   │   ├── WhitelistSection.svelte # User whitelist (Settings tab)
│   │   │   │   ├── CustomBlockSection.svelte # Custom blocks (Settings tab)
│   │   │   │   ├── RecentBonks.svelte   # Activity logs (Logs tab)
│   │   │   │   ├── BottomNav.svelte     # Tab navigation
│   │   │   │   └── Notification.svelte # Toast notifications
│   │   │   └── stores.ts    # Svelte stores for state management
│   │   ├── main.ts          # Application entry point
│   │   ├── app.css          # Global styles
│   │   ├── theme.css        # Theme variables
│   │   └── fonts.css        # Font imports
│   ├── static/              # Static assets (images, icons)
│   ├── index.html           # Main HTML template
│   ├── package.json         # Dependencies and scripts
│   ├── vite.config.ts       # Vite configuration
│   ├── svelte.config.js     # Svelte configuration
│   └── tsconfig.json        # TypeScript configuration
├── backend/                  # Backend services and infrastructure
│   ├── log-platform/        # Unified Rust logging platform (Cargo workspace)
│   │   ├── src/
│   │   │   ├── lib.rs       # Shared types (LogEvent, Service, LogMeta, Trace)
│   │   │   ├── ingestd.rs   # HTTP log ingestion service binary
│   │   │   └── alertd.rs    # Spam detection + monitoring binary
│   │   ├── Dockerfile.ingestd   # Multi-stage build for ingestd
│   │   ├── Dockerfile.alertd    # Multi-stage build for alertd
│   │   └── Cargo.toml       # Unified workspace dependencies
│   ├── init/                # OpenSearch initialization
│   │   ├── init.sh          # Setup script for indices and policies
│   │   ├── index-template.json  # ECS-compliant field mappings
│   │   └── ism-policy.json  # 7-day retention policy
│   ├── docker-compose.yml   # Full stack: OpenSearch, Dashboards, ingestd, alertd
│   └── README.md            # Backend documentation
├── bot/                      # Telegram bot service (planned)
│   └── requirements.txt
├── redis-example/            # Redis Streams Producer/Worker prototype
├── docker-compose.yml        # Local development environment
├── docs/                     # Project documentation
├── scripts/                  # Deployment and utility scripts
└── .kiro/                    # Kiro CLI configuration
```

## File Naming Conventions
**Frontend**: PascalCase for Svelte components, kebab-case for CSS files, camelCase for TypeScript
**Backend**: snake_case for Python files and functions
**Rust**: snake_case for files, PascalCase for structs and enums
**Database**: snake_case for table and column names
**API Endpoints**: kebab-case for URLs, camelCase for JSON fields

## Module Organization
**Frontend**: Component-based organization with centralized state management via Svelte stores
**Backend**: Unified Rust workspace with shared library (lib.rs) and multiple binaries (ingestd, alertd)
**Log Platform**: Cargo workspace architecture with shared types and separate service binaries
**Bot**: Handler-based organization by message type and command (planned)
**Rust**: Module-per-feature with clear separation of concerns, multi-stage Docker builds

## Configuration Files
**Environment**: `.env` files for each service with environment-specific settings
**Docker**: `docker-compose.yml` for local development, separate production configs
**Database**: Migration files in `backend/migrations/`
**CI/CD**: `.github/workflows/` for GitHub Actions

## Documentation Structure
**API Documentation**: OpenAPI/Swagger specs in `docs/api/`
**User Documentation**: Markdown files in `docs/user/`
**Developer Documentation**: Setup and contribution guides in `docs/dev/`
**Architecture Diagrams**: Visual documentation in `docs/architecture/`

## Asset Organization
**Frontend Assets**: Static files in `frontend/static/`
**Bot Assets**: Images and media in `bot/assets/`
**Documentation Assets**: Screenshots and diagrams in `docs/assets/`

## Build Artifacts
**Frontend**: Built files in `frontend/build/`
**Backend**: Docker images and compiled Python bytecode
**Rust**: Compiled binaries in `spam-detector/target/`
**Deployment**: Packaged containers and deployment manifests

## Environment-Specific Files
**Development**: `docker-compose.dev.yml`, `.env.dev`
**Staging**: `docker-compose.staging.yml`, `.env.staging`
**Production**: Kubernetes manifests, `.env.prod`
**Testing**: Test-specific configurations and mock data
