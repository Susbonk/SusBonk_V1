# SusBonk Django Admin Panel

Django-based web interface for managing the SusBonk PostgreSQL database.

## Features

- Full CRUD operations on all database tables
- UUID-based primary keys with automatic generation
- PostgreSQL triggers for automatic `updated_at` timestamps
- Pre-configured admin interface with search and filters
- Docker deployment with automatic migrations
- Default prompts and runtime statistics

## Structure

```
admin/
├── core/                   # Django app
│   ├── migrations/         # Database migrations
│   │   ├── 0001_initial.py       # Schema creation
│   │   └── 0002_default_data.py  # Default prompts
│   ├── models_base.py      # BaseModel abstract class
│   ├── models.py           # All database models
│   └── admin.py            # Admin configurations
├── db_admin/               # Django project
│   ├── settings.py         # Configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI application
├── manage.py               # Django management
├── start.sh                # Startup script
├── Dockerfile              # Container definition
└── pyproject.toml          # Dependencies
```

## Models

- **User**: User accounts with platform-specific IDs (Telegram, Discord)
- **Chat**: Chat configurations with AI settings and statistics
- **Prompt**: Pre-made spam detection prompts
- **CustomPrompt**: User-created custom prompts
- **UserState**: User state tracking per chat
- **ChatPrompt**: Many-to-many link between chats and prompts
- **ChatCustomPrompt**: Many-to-many link between chats and custom prompts
- **RuntimeStatistics**: System-wide statistics

## Quick Start

### Prerequisites

- Python 3.13 (specified in `.python-version`)
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL 14+

### Local Development

```bash
# Install dependencies with uv (uses uv.lock for reproducible builds)
cd admin
uv sync

# Set environment variables
export POSTGRES_DB=postgres
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Start server
uv run python manage.py runserver 0.0.0.0:8090
```

### Dependency Management

This project uses `uv` for dependency management:
- `pyproject.toml`: Declares dependencies
- `uv.lock`: Locks exact versions for reproducibility
- `.python-version`: Pins Python version to 3.13

To update dependencies:
```bash
# Add new dependency
uv add <package>

# Update all dependencies
uv lock --upgrade

# Sync environment with lockfile
uv sync
```

### Docker Deployment

```bash
# From project root
docker-compose up -d admin

# Access admin panel
open http://localhost:8090/admin
```

Default superuser credentials (created automatically):
- Username: `admin`
- Password: `admin`

## Service Dependencies

The admin service depends on:
1. **pg-database**: PostgreSQL database (must be healthy)
2. **db-init**: Schema initialization (must complete successfully)

Dependency chain: `pg-database` → `db-init` → `admin`

## Environment Variables

Required variables (from `.env`):
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_HOST`: Database host (default: `pg-database`)
- `POSTGRES_PORT`: Database port (default: `5432`)

Optional:
- `JWT_SECRET`: Django secret key (default: auto-generated)

## Database Schema Management

Django fully manages the database schema:
- Migrations create tables, indexes, constraints, and triggers
- `auto_now=True` on `updated_at` fields (Django-level)
- PostgreSQL triggers also update `updated_at` (database-level redundancy)
- UUID extension automatically enabled

## Admin Interface Features

Each model has:
- **List display**: Key fields shown in table view
- **Search**: Full-text search on relevant fields
- **Filters**: Filter by status, dates, and relationships
- **Inline editing**: Edit related objects inline (where applicable)

## Migrations

### Create new migration
```bash
python manage.py makemigrations
```

### Apply migrations
```bash
python manage.py migrate
```

### View migration SQL
```bash
python manage.py sqlmigrate core 0001
```

## Troubleshooting

### Database connection errors
- Ensure PostgreSQL is running: `docker-compose ps pg-database`
- Check environment variables are set correctly
- Verify network connectivity: `docker network inspect backend_db-net`

### Migration errors
- Reset migrations: `python manage.py migrate core zero`
- Drop database and recreate: `docker-compose down -v && docker-compose up -d`

### Admin panel not accessible
- Check container logs: `docker logs susbonk-admin`
- Verify port 5000 is not in use: `lsof -i :5000`
- Ensure dependencies started: `docker-compose ps`

## Development

### Add new model
1. Add model to `core/models.py`
2. Register in `core/admin.py`
3. Create migration: `python manage.py makemigrations`
4. Apply migration: `python manage.py migrate`

### Customize admin interface
Edit `core/admin.py` to add:
- Custom list displays
- Search fields
- Filters
- Actions
- Inline editors

## Security Notes

- Change default superuser password in production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` properly
- Use strong `SECRET_KEY` from environment
- CSRF protection is enabled by default
- Consider adding SSL/TLS for production

## Port

- Admin panel: `http://localhost:8090/admin`

## Lockfile Policy

This project uses `uv.lock` for deterministic dependency resolution:
- **Committed to git**: Yes, `uv.lock` is version controlled
- **Updated when**: Dependencies change in `pyproject.toml`
- **Docker builds**: Use `uv sync --frozen` to ensure exact versions
- **CI/CD**: Always use lockfile for reproducible builds
