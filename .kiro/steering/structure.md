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
├── backend/                  # Python API server
│   ├── src/
│   │   ├── api/             # FastAPI routes and endpoints
│   │   ├── models/          # Database models and schemas
│   │   ├── services/        # Business logic and external integrations
│   │   ├── utils/           # Helper functions and utilities
│   │   └── main.py          # Application entry point
│   ├── tests/               # Backend tests
│   ├── requirements.txt     # Python dependencies
│   ├── schema.sql           # PostgreSQL database schema
│   └── Dockerfile
├── bot/                      # Telegram bot service
│   ├── src/
│   │   ├── handlers/        # Message and command handlers
│   │   ├── middleware/      # Bot middleware and filters
│   │   ├── utils/           # Bot utilities and helpers
│   │   └── main.py          # Bot entry point
│   ├── tests/
│   └── requirements.txt
├── ingestd/                  # Rust message ingestion service
│   ├── src/
│   │   ├── ingestion/       # High-speed message ingestion
│   │   ├── models/          # Data structures and schemas
│   │   ├── api/             # HTTP API for ingestion service
│   │   └── main.rs          # Rust service entry point
│   ├── tests/
│   └── Cargo.toml
├── alertd/                   # Rust spam detection + monitoring service
│   ├── src/
│   │   ├── detection/       # Spam detection algorithms
│   │   ├── monitoring/      # Infrastructure monitoring
│   │   ├── alerts/          # Email and notification handling
│   │   ├── models/          # ML models and data structures
│   │   ├── api/             # HTTP API for detection service
│   │   └── main.rs          # Rust service entry point
│   ├── tests/
│   └── Cargo.toml
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
**Backend**: Layered architecture (API → Services → Models → Database)
**Bot**: Handler-based organization by message type and command
**Rust**: Module-per-feature with clear separation of concerns

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
