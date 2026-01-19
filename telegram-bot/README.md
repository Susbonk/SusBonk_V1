# SusBonk Telegram Bot

A standalone Rust-based Telegram bot for spam detection and link analysis.

## Quick Start

```bash
# Build and run
cd telegram-bot
cargo run --bin telegram-bot

# Or with Docker
docker build -f telegram-bot/Dockerfile . -t susbonk-telegram-bot
docker run susbonk-telegram-bot
```

## Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"
export REDIS_URL="redis://localhost:6379"
export INGEST_URL="http://localhost:8080"
```

## Features

- **Silent Spam Detection**: Monitors messages for suspicious links
- **Link Analysis**: Detects shortened URLs, suspicious domains
- **Admin Controls**: `/enable` and `/disable` commands for group admins
- **Redis Streams Logging**: Events logged for analysis
- **Database Integration**: Per-group configuration with PostgreSQL
- **Health Monitoring**: Health check endpoint at `/health`

## Architecture

This is a standalone Cargo workspace separate from the main SusBonk log-platform. It includes:

- `config/` - Centralized configuration management with global CONFIG static
- `telegram-bot/` - Main bot binary
  - `src/types.rs` - Shared data structures
  - `src/database.rs` - PostgreSQL integration
  - `src/link_detector.rs` - URL analysis engine
  - `src/redis_client.rs` - Redis Streams client
  - `src/log_client.rs` - Log platform integration

## Configuration

All configuration is managed through the `config` crate using environment variables:

```rust
use config::CONFIG;

// Access configuration anywhere
let token = &CONFIG.telegram.token;
let db_url = CONFIG.database.connection_string();
```

See `config/README.md` for full documentation on environment variables and settings.

## Integration

The bot integrates with the SusBonk ecosystem via:
- **PostgreSQL**: Uses existing `chats` table for configuration
- **Redis Streams**: Logs spam events for analysis
- **Log Platform**: Sends structured logs to ingestd service
- **Docker Compose**: Included in main SusBonk deployment

See the main README.md for comprehensive documentation.
