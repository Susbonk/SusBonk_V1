# OpenSearch Logging System

## Overview
Rust-based logging system using OpenSearch for observability in the SusBonk backend.

## Components
- **alertd**: Rust service for spam detection + monitoring + logging
- **OpenSearch**: Document store for logs and analytics
- **OpenSearch Dashboards**: Web UI for log visualization

## Quick Start

### Development
```bash
cd backend
docker-compose up -d
```

### Access
- OpenSearch: http://localhost:9200
- Dashboards: http://localhost:5601

### Environment Variables
- `OPENSEARCH_URL`: OpenSearch endpoint (default: http://localhost:9200)
- `INDEX_PREFIX`: Index prefix for logs (default: susbonk)
- `RUST_LOG`: Log level (default: info)

## Log Types
- **Application logs**: General service logs
- **Spam detection**: Message analysis results
- **Monitoring**: System metrics and health

## Index Patterns
- `{prefix}-logs-YYYY-MM`: Application logs
- `{prefix}-spam-YYYY-MM`: Spam detection events
- `{prefix}-metrics-YYYY-MM`: Monitoring metrics
