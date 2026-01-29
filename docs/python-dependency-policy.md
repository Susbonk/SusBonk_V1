# Python Version and Dependency Management Policy

## Python Version Management

**Standard**: `.python-version` file (pyenv/asdf compatible)

### Current Version
- **Python 3.13** (specified in `.python-version`)

### Policy
- All Python services use the same Python version
- `.python-version` file is committed to git
- Local development tools (pyenv, asdf) automatically use this version
- Docker images explicitly use `python:3.13-slim` base image

### Services Using Python
- `admin/` - Django admin panel
- `backend/` - FastAPI backend
- `telegram-bot/` - Telegram bot service
- `ai-service/` - AI inference service

## Dependency Management

**Standard**: `uv` package manager with lockfiles

### Lockfile Strategy
- **Tool**: [uv](https://github.com/astral-sh/uv) by Astral
- **Lockfile**: `uv.lock` (committed to git)
- **Declaration**: `pyproject.toml` (PEP 621 compliant)

### Workflow

#### Adding Dependencies
```bash
cd <service-directory>
uv add <package-name>
# This updates both pyproject.toml and uv.lock
```

#### Updating Dependencies
```bash
# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package <package-name>
```

#### Installing Dependencies
```bash
# Development (respects lockfile)
uv sync

# Production/CI (strict lockfile enforcement)
uv sync --frozen
```

### Docker Integration

All Dockerfiles follow this pattern:
```dockerfile
FROM python:3.13-slim
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock .python-version ./

# Install uv and dependencies
RUN pip install --no-cache-dir uv && \
    uv sync --frozen

# Copy application code
COPY . .
```

**Key points:**
- `--frozen` flag ensures exact versions from lockfile
- Fails build if lockfile is out of sync with pyproject.toml
- Guarantees reproducible builds

### CI/CD Policy

- **Always use lockfiles**: `uv sync --frozen` in all CI pipelines
- **Lockfile validation**: CI should fail if lockfile is outdated
- **Dependency updates**: Automated PRs via Dependabot/Renovate (optional)

### Version Control

**Committed files:**
- ✅ `.python-version`
- ✅ `pyproject.toml`
- ✅ `uv.lock`

**Ignored files:**
- ❌ `.venv/` (virtual environments)
- ❌ `__pycache__/` (Python bytecode)
- ❌ `*.pyc` (compiled Python files)

## Migration from Other Tools

### From pip + requirements.txt
```bash
# Convert requirements.txt to pyproject.toml
uv add $(cat requirements.txt)

# Generate lockfile
uv lock
```

### From Poetry
```bash
# uv can read pyproject.toml from Poetry
uv sync

# Generate uv.lock
uv lock
```

### From Pipenv
```bash
# Export Pipfile to requirements.txt
pipenv requirements > requirements.txt

# Import to uv
uv add $(cat requirements.txt)
```

## Troubleshooting

### Lockfile out of sync
```bash
# Regenerate lockfile
uv lock

# Or update to latest compatible versions
uv lock --upgrade
```

### Python version mismatch
```bash
# Check current Python version
python --version

# Install correct version with pyenv
pyenv install 3.13
pyenv local 3.13
```

### Docker build failures
```bash
# Ensure lockfile is up to date
uv lock

# Rebuild without cache
docker-compose build --no-cache <service-name>
```

## Benefits of This Approach

1. **Reproducibility**: Exact same dependencies across all environments
2. **Speed**: uv is significantly faster than pip
3. **Standards**: Uses PEP 621 (pyproject.toml) and modern Python packaging
4. **Simplicity**: Single tool for dependency management
5. **Safety**: `--frozen` flag prevents accidental dependency changes in production
