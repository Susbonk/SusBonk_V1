# Log Platform Workspace Refactor

## Overview
Refactored the log-platform from a single crate with multiple binaries into a proper Cargo workspace with shared common library and enhanced monitoring capabilities.

## Phase 1: Workspace Structure

### New Directory Layout
```
log-platform/
├── Cargo.toml                    # Workspace root
├── log_platform_common/          # Shared library
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── types.rs              # Shared types (LogEvent, Service, etc.)
│       ├── env.rs                # Environment helpers
│       ├── http.rs               # HTTP client factory
│       ├── opensearch.rs         # OpenSearch client wrapper
│       └── notify/
│           └── mod.rs            # Notification system
├── ingestd/                      # Log ingestion service
│   ├── Cargo.toml
│   └── src/
│       └── main.rs
├── alertd/                       # Monitoring & alerting service
│   ├── Cargo.toml
│   └── src/
│       └── main.rs
├── Dockerfile.ingestd
└── Dockerfile.alertd
```

## Phase 2: Common Library Components

### `log_platform_common/src/types.rs`
- `LogEvent` - ECS-compliant log event structure
- `Service`, `LogMeta`, `Trace` - Nested structures
- `IngestPayload` - Single or batch log ingestion
- `IngestResponse` - Ingestion result

### `log_platform_common/src/env.rs`
Environment variable helpers with defaults:
- `get_opensearch_url()` - OpenSearch connection
- `get_ingest_url()` - Log ingestion endpoint
- `get_port()` - Service port
- `get_smtp_host()`, `get_smtp_port()` - Email configuration
- `get_alert_email()` - Alert recipient

### `log_platform_common/src/http.rs`
HTTP client factory with 30-second timeout

### `log_platform_common/src/opensearch.rs`
OpenSearch client wrapper:
- `bulk_index()` - Bulk log indexing with daily indices
- `search()` - Query execution
- `base_url()` - URL accessor

### `log_platform_common/src/notify/mod.rs`
Notification system with trait-based design:
- `Notifier` trait - Async notification interface
- `LogNotifier` - Logs alerts to stdout
- `EmailNotifier` - Email alerts (stub implementation)
- `MultiNotifier` - Composite pattern for multiple notifiers

## Phase 3: Enhanced Alertd

### New Monitoring Functions

#### `check_disk()`
- Queries OpenSearch for total disk usage
- Alerts if usage exceeds 50 GB threshold
- Logs disk usage metrics

#### `check_readonly()`
- Checks all `logs-*` indices for read-only status
- Alerts when indices become read-only (disk full)
- Logs read-only alerts with index names

#### `check_log_warnings_errors(warn_threshold, error_threshold)`
- Counts warnings and errors in last 5 minutes
- Configurable thresholds (default: 100 warns, 50 errors)
- Alerts when thresholds exceeded
- Logs threshold violations with counts

### Monitoring Loop
- Runs every 60 seconds
- Executes all health checks
- Logs failures without crashing
- Uses MultiNotifier for alerts (log + email)

## Docker Updates

### Dockerfile.ingestd
```dockerfile
COPY Cargo.toml ./
COPY log_platform_common ./log_platform_common
COPY ingestd ./ingestd
RUN cargo build --release --bin ingestd
```

### Dockerfile.alertd
```dockerfile
COPY Cargo.toml ./
COPY log_platform_common ./log_platform_common
COPY alertd ./alertd
RUN cargo build --release --bin alertd
ENV INGEST_URL=http://log-ingest:8080
```

## Benefits

### Code Reuse
- Shared types eliminate duplication
- Common utilities (env, http, opensearch)
- Consistent error handling

### Maintainability
- Clear separation of concerns
- Single source of truth for types
- Easier to add new services

### Extensibility
- Notification system supports multiple channels
- Easy to add new monitoring checks
- Pluggable architecture

### Monitoring
- Proactive disk space alerts
- Read-only index detection
- Log level threshold monitoring
- Multi-channel notifications

## Environment Variables

### Required
- `OPENSEARCH_URL` - OpenSearch endpoint (default: http://localhost:9200)
- `INGEST_URL` - Log ingestion endpoint (default: http://localhost:8080)

### Optional
- `PORT` - Service port (default: 8080)
- `SMTP_HOST` - Email server (default: localhost)
- `SMTP_PORT` - Email port (default: 587)
- `ALERT_EMAIL` - Alert recipient (default: admin@example.com)

## Usage

### Build Workspace
```bash
cd log-platform
cargo build --release
```

### Build Docker Images
```bash
docker build -f Dockerfile.ingestd -t ingestd:latest .
docker build -f Dockerfile.alertd -t alertd:latest .
```

### Run Services
```bash
# Ingestd
docker run -p 8080:8080 \
  -e OPENSEARCH_URL=http://os01:9200 \
  ingestd:latest

# Alertd
docker run \
  -e OPENSEARCH_URL=http://os01:9200 \
  -e INGEST_URL=http://log-ingest:8080 \
  -e ALERT_EMAIL=ops@example.com \
  alertd:latest
```

## Migration Notes

### Breaking Changes
- Old `src/lib.rs`, `src/ingestd.rs`, `src/alertd.rs` replaced by workspace structure
- Import paths changed from `log_platform::*` to `log_platform_common::*`

### Backward Compatibility
- API endpoints unchanged
- Log format unchanged (ECS-compliant)
- Environment variables backward compatible

## Next Steps

1. Implement actual email sending in `EmailNotifier`
2. Add Slack/Discord notifiers
3. Add more monitoring checks (CPU, memory, query latency)
4. Add configuration file support for thresholds
5. Add metrics export (Prometheus)
6. Add health check endpoints to alertd
