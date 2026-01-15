# Log Platform Workspace - Quick Reference

## 📁 Structure
```
log-platform/
├── Cargo.toml                          # Workspace root with shared dependencies
│
├── log_platform_common/                # 📦 Shared Library
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs                      # Module exports
│       ├── types.rs                    # LogEvent, Service, IngestPayload
│       ├── env.rs                      # Environment variable helpers
│       ├── http.rs                     # HTTP client factory
│       ├── opensearch.rs               # OpenSearch client wrapper
│       └── notify/
│           └── mod.rs                  # Notification system (MultiNotifier)
│
├── ingestd/                            # 🔵 Log Ingestion Service
│   ├── Cargo.toml
│   ├── Dockerfile.ingestd
│   └── src/
│       └── main.rs                     # HTTP server on :8080, /ingest endpoint
│
└── alertd/                             # 🔴 Monitoring & Alerting Service
    ├── Cargo.toml
    ├── Dockerfile.alertd
    └── src/
        └── main.rs                     # Spam detection + infrastructure monitoring
```

## 🔧 Common Library API

### Types (`log_platform_common::types`)
```rust
LogEvent {
    timestamp: Option<DateTime<Utc>>,
    service: Option<Service>,
    log: Option<LogMeta>,
    message: Option<String>,
    trace: Option<Trace>,
    labels: Option<Value>,
    fields: Option<Value>,
}

IngestPayload::Single(LogEvent) | IngestPayload::Batch(Vec<LogEvent>)
```

### Environment (`log_platform_common::env`)
```rust
get_opensearch_url() -> String      // Default: http://localhost:9200
get_ingest_url() -> String          // Default: http://localhost:8080
get_port() -> u16                   // Default: 8080
get_smtp_host() -> String           // Default: localhost
get_smtp_port() -> u16              // Default: 587
get_alert_email() -> String         // Default: admin@example.com
```

### HTTP (`log_platform_common::http`)
```rust
create_client() -> Client           // 30-second timeout
```

### OpenSearch (`log_platform_common::opensearch`)
```rust
OpenSearchClient::new(base_url: String)
    .bulk_index(events: Vec<LogEvent>) -> Result<()>
    .search(index: &str, query: Value) -> Result<Value>
    .base_url() -> &str
```

### Notifications (`log_platform_common::notify`)
```rust
trait Notifier {
    async fn send(&self, subject: &str, message: &str) -> Result<()>
}

LogNotifier                         // Logs to stdout
EmailNotifier::new(host, port, to)  // Email alerts
MultiNotifier::new()                // Composite notifier
    .add(Box<dyn Notifier>)
    .send(subject, message)
```

## 🔵 Ingestd Service

### Endpoints
- `POST /ingest` - Ingest single or batch logs
- `GET /health` - Health check

### Behavior
- Accepts `IngestPayload` (single or batch)
- Bulk indexes to OpenSearch
- Daily indices: `logs-{service}-{YYYY.MM.DD}`
- Returns `IngestResponse { indexed: usize }`

## 🔴 Alertd Service

### Monitoring Functions

#### `check_disk()`
- Queries total disk usage
- **Threshold**: 50 GB
- **Alert**: "High disk usage: X.XX GB"

#### `check_readonly()`
- Checks `logs-*` indices for read-only status
- **Alert**: "Index {name} is read-only"

#### `check_log_warnings_errors(warn_threshold, error_threshold)`
- Counts warnings/errors in last 5 minutes
- **Default thresholds**: 100 warns, 50 errors
- **Alert**: "X errors in last 5 minutes (threshold: Y)"

### Monitoring Loop
- Runs every **60 seconds**
- Executes all health checks
- Logs via ingestd HTTP API
- Sends alerts via MultiNotifier

## 🐳 Docker

### Build
```bash
docker build -f Dockerfile.ingestd -t ingestd:latest .
docker build -f Dockerfile.alertd -t alertd:latest .
```

### Run Ingestd
```bash
docker run -p 8080:8080 \
  -e OPENSEARCH_URL=http://os01:9200 \
  ingestd:latest
```

### Run Alertd
```bash
docker run \
  -e OPENSEARCH_URL=http://os01:9200 \
  -e INGEST_URL=http://log-ingest:8080 \
  -e ALERT_EMAIL=ops@example.com \
  alertd:latest
```

## 🔄 Migration from Old Structure

### Before (Single Crate)
```
log-platform/
├── Cargo.toml
└── src/
    ├── lib.rs          # Shared types
    ├── ingestd.rs      # Binary
    └── alertd.rs       # Binary
```

### After (Workspace)
```
log-platform/
├── Cargo.toml                      # [workspace]
├── log_platform_common/            # Shared library
├── ingestd/                        # Service crate
└── alertd/                         # Service crate
```

### Import Changes
```rust
// Before
use log_platform::{LogEvent, Service};

// After
use log_platform_common::{LogEvent, Service};
```

## 📊 Monitoring Thresholds

| Check | Interval | Threshold | Alert Level |
|-------|----------|-----------|-------------|
| Disk Usage | 60s | 50 GB | Warning |
| Read-Only Indices | 60s | Any | Error |
| Warning Logs | 60s | 100/5min | Warning |
| Error Logs | 60s | 50/5min | Warning |

## 🚀 Development

### Build Workspace
```bash
cd log-platform
cargo build --release
```

### Run Locally
```bash
# Terminal 1: Ingestd
cargo run --bin ingestd

# Terminal 2: Alertd
cargo run --bin alertd
```

### Test
```bash
# Send test log
curl -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "service": {"name": "test"},
    "log": {"level": "info"},
    "message": "Test log"
  }'
```

## 📝 Key Features

✅ **Workspace Architecture** - Shared dependencies, clean separation  
✅ **Common Library** - Reusable types, clients, utilities  
✅ **OpenSearch Integration** - Bulk indexing, daily indices  
✅ **Multi-Channel Notifications** - Log, email, extensible  
✅ **Infrastructure Monitoring** - Disk, read-only, log thresholds  
✅ **ECS-Compliant Logs** - Standard schema, @timestamp, nested fields  
✅ **Docker Multi-Stage Builds** - Optimized images  
✅ **Environment-Based Config** - 12-factor app principles
