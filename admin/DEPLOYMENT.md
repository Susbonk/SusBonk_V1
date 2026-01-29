# SusBonk Admin Service

Django admin interface for managing SusBonk database entities.

## Features

- User management (Telegram/Discord users)
- Chat configuration and moderation settings
- Prompt management (pre-made and custom)
- Runtime statistics monitoring
- Automatic database triggers for `updated_at` fields

## Database Triggers

The admin service automatically installs PostgreSQL triggers on first migration:

- **`set_updated_at()`**: Trigger function that updates `updated_at` on row UPDATE
- Applied to all tables: `users`, `chats`, `prompts`, `custom_prompts`, `user_states`, `chat_prompts`, `chat_custom_prompts`, `runtime_statistics`

This ensures `updated_at` is maintained at the database level without application code.

## Deployment Options

### WSGI (Default - Development)

```bash
python manage.py runserver 0.0.0.0:8090
```

Used by default in `start.sh` for local development.

### ASGI (Production)

For production deployments with async support:

```bash
uvicorn db_admin.asgi:application --host 0.0.0.0 --port 8090
```

Or with Gunicorn + Uvicorn workers:

```bash
gunicorn db_admin.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8090
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `postgres` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `password` | Database password |
| `POSTGRES_HOST` | `pg-database` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `JWT_SECRET` | `django-insecure-dev-key-change-in-production` | Django secret key |
| `DJANGO_SUPERUSER_USERNAME` | `admin` | Initial superuser username |
| `DJANGO_SUPERUSER_EMAIL` | `admin@susbonk.local` | Initial superuser email |
| `DJANGO_SUPERUSER_PASSWORD` | `admin` | Initial superuser password |

## Migrations

The service includes migrations for:

1. **0001_initial**: Initial schema with all models
2. **0002_default_data**: Default prompts and runtime statistics
3. **0003_runtimestatistics_chat_messages_deleted**: Add chat message deletion counter
4. **0004_server_side_defaults**: Set PostgreSQL server-side defaults for timestamps
5. **0005_chat_field_updates**: Update chat fields (allowed_mentions, cleanup field renames, remove threshold fields)

Run migrations:

```bash
python manage.py migrate
```

## Local Development

```bash
# Install dependencies
uv sync

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver 0.0.0.0:8090
```

## Docker

```bash
# Build
docker build -t susbonk-admin .

# Run
docker run -p 8090:8090 \
  -e POSTGRES_HOST=postgres \
  -e POSTGRES_DB=susbonk \
  -e POSTGRES_USER=susbonk \
  -e POSTGRES_PASSWORD=susbonk_dev \
  susbonk-admin
```

## Access

- URL: http://localhost:8090/admin
- Default credentials: `admin` / `admin` (change in production)

## Python Version Management

This service uses Python 3.13 as specified in `.python-version`. Dependencies are locked with `uv.lock` for reproducible builds.

To update dependencies:

```bash
# Add new dependency
uv add package-name

# Update all dependencies
uv lock --upgrade

# Sync environment
uv sync
```
