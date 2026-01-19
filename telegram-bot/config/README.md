# Config Crate

Centralized configuration management for the SusBonk Telegram Bot.

## Features

- **Global Static Config**: Single source of truth using `once_cell::Lazy`
- **Environment Variable Loading**: Reads from `.env` file or environment
- **Type-Safe Settings**: Strongly typed configuration structs
- **Sensible Defaults**: Falls back to reasonable defaults when variables not set

## Usage

```rust
use config::CONFIG;

fn main() {
    // Access configuration anywhere in your code
    println!("Bot token: {}", CONFIG.telegram.token);
    println!("Database: {}", CONFIG.database.connection_string());
    println!("Run mode: {:?}", CONFIG.run_mode);
}
```

## Environment Variables

### Required
- `TELOXIDE_TOKEN` or `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name

### Optional (with defaults)
- `RUN_MODE` - `polling` (default) or `webhook`
- `POSTGRES_HOST` - Default: `localhost`
- `POSTGRES_PORT` - Default: `5432`
- `POSTGRES_MAX_CONNECTIONS` - Default: `10`
- `POSTGRES_MIN_CONNECTIONS` - Default: `1`
- `REDIS_URL` - Default: `redis://localhost:6379`
- `TELEGRAM_BOT_USERNAME` - Bot username (optional)
- `WEBHOOK_URL` - Webhook URL (required if `RUN_MODE=webhook`)
- `WEBHOOK_PORT` - Default: `8443`
- `LOG_LEVEL` - Default: `info`
- `INGEST_URL` or `OS_INGEST_URL` - Default: `http://localhost:8080`
- `HEALTH_PORT` - Default: `8081`

## Configuration Structs

### `Config`
Main configuration container with all settings.

### `RunMode`
```rust
pub enum RunMode {
    Polling,   // Long polling (default)
    Webhook,   // Webhook mode
}
```

### `DatabaseSettings`
PostgreSQL connection settings with helper method:
```rust
let connection_string = CONFIG.database.connection_string();
// Returns: "postgresql://user:pass@host:port/db"
```

### `RedisSettings`
Redis connection URL.

### `TelegramSettings`
Bot token and optional username.

### `WebhookSettings`
Webhook URL and port (used when `RUN_MODE=webhook`).

### `LogSettings`
Logging level and ingest service URL.

## Example `.env`

```bash
# Required
TELOXIDE_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=susbonk

# Optional
RUN_MODE=polling
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_URL=redis://localhost:6379
LOG_LEVEL=info
HEALTH_PORT=8081
```
