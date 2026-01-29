# OpenSearch Alert Engine – Usage Instructions

## Overview

This service periodically checks an OpenSearch cluster and sends alerts when:

* Disk space on nodes is below configured thresholds
* Indices are switched to `read_only_allow_delete`
* Errors or warnings appear in logs within a recent time window

Alerts are delivered to:

* stdout (always)
* email (optional, via SMTP)

The service is designed to run continuously as a daemon or container.

---

## Requirements

* Rust 1.72+ (or a prebuilt binary)
* Network access to OpenSearch
* (Optional) SMTP credentials for email alerts

---

## Configuration

All configuration is done via **environment variables**.

### Core OpenSearch Settings

| Variable             | Description               | Default                 |
| -------------------- | ------------------------- | ----------------------- |
| `OPENSEARCH_URL`     | OpenSearch base URL       | `http://localhost:9200` |
| `LOG_INDEX_PATTERN`  | Index pattern for logs    | `logs-*`                |
| `ALERT_INTERVAL_SEC` | Check interval in seconds | `30`                    |

---

### Disk Space Thresholds

| Variable       | Description                   | Default |
| -------------- | ----------------------------- | ------- |
| `MIN_FREE_GB`  | Minimum free disk space in GB | `15.0`  |
| `MIN_FREE_PCT` | Minimum free disk percentage  | `12.0`  |

An alert with severity `CRIT` is sent if **either** threshold is violated.

---

### Log Alert Thresholds

Log checks operate on a **sliding time window of the last 5 minutes**.

| Variable            | Description                                      | Default |
| ------------------- | ------------------------------------------------ | ------- |
| `ERROR_THRESHOLD`   | Minimum number of errors to trigger CRIT alert   | `1`     |
| `WARNING_THRESHOLD` | Minimum number of warnings to trigger WARN alert | `5`     |

**Error detection includes:**

* `log.level` = `ERROR`, `CRITICAL`, `FATAL`
* message contains `error`, `exception`, or `critical`

**Warning detection includes:**

* `log.level` = `WARN`, `WARNING`
* message contains `warn` or `warning`

---

### Email Alerts (Optional)

Email alerts are disabled by default.

To enable them:

```env
EMAIL_ENABLED=1
```

#### Required SMTP Variables

| Variable           | Description                          |
| ------------------ | ------------------------------------ |
| `SMTP_SERVER`      | SMTP server hostname                 |
| `SMTP_PORT`        | SMTP port (usually `587` or `465`)   |
| `SMTP_USER`        | SMTP username                        |
| `SMTP_PASSWORD`    | SMTP password                        |
| `ALERT_EMAIL_TO`   | Recipient email                      |
| `ALERT_EMAIL_FROM` | Sender email (defaults to SMTP_USER) |

#### Example

```env
EMAIL_ENABLED=1
SMTP_SERVER=smtp.yandex.ru
SMTP_PORT=465
SMTP_USER=ivan.vered@ya.ru
SMTP_PASSWORD=********
ALERT_EMAIL_TO=ivan.vered@gmail.com
ALERT_EMAIL_FROM=ivan.vered@ya.ru
```

> ⚠️ **Never commit credentials** to git.
> Use `.env`, Docker secrets, or your deployment secret manager.

---

## Running the Service

### Local Run

```bash
export OPENSEARCH_URL=http://localhost:9200
export EMAIL_ENABLED=0

cargo run --release
```

### Using `.env`

```bash
set -a
source .env
set +a

cargo run --release
```

---

## Runtime Behavior

* The service runs in an infinite loop.
* Each iteration performs:

  1. Disk space check
  2. Read-only index check
  3. Log error & warning checks
* Alerts are emitted immediately.
* SMTP sending is executed in a background thread and **never blocks** checks.

---

## Logging

* Uses `tracing`
* Default log level: `INFO`
* Output is written to stdout (suitable for Docker / systemd)

---

## Extending the System

The architecture is intentionally modular.

### Easy extensions:

* Add a `TelegramNotifier`
* Add cooldown / deduplication
* Add new checks (cluster health, JVM pressure, shard state)

### Key extension points:

* `Notifier` trait
* `check_*` functions
* `Alert` model

---

## Notes & Caveats

* Log alerts are **time-bounded** (last 5 minutes only)
* Thresholds prevent alert spam but do not deduplicate messages
* SMTP port `465` uses implicit TLS — if email fails, verify SMTP TLS mode
