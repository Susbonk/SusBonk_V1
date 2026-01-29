# Python Dependency Management - Quick Reference

## Files Required (Per Service)

```
service/
├── .python-version          # Python version (3.13)
├── pyproject.toml          # Dependency declarations
└── uv.lock                 # Locked versions
```

## Common Commands

### Development
```bash
# Install dependencies
uv sync

# Add new package
uv add <package>

# Add dev dependency
uv add --dev <package>

# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package <package>
```

### Production/CI
```bash
# Install with strict lockfile enforcement
uv sync --frozen

# This fails if lockfile is out of sync
```

### Docker
```dockerfile
# Copy dependency files
COPY pyproject.toml uv.lock .python-version ./

# Install with frozen lockfile
RUN uv sync --frozen
```

## Troubleshooting

### "Lockfile is out of date"
```bash
uv lock
```

### "Python version mismatch"
```bash
pyenv install 3.13
pyenv local 3.13
```

### "Package not found"
```bash
uv add <package>
```

## Policy Summary

✅ **DO**
- Commit `.python-version`, `pyproject.toml`, and `uv.lock`
- Use `uv sync --frozen` in Docker and CI
- Update lockfile explicitly with `uv lock --upgrade`
- Document dependency changes in commit messages

❌ **DON'T**
- Manually edit `uv.lock`
- Use `pip install` directly
- Commit `.venv/` directories
- Skip lockfile in production builds

## Service Status

| Service | .python-version | uv.lock | Dockerfile |
|---------|----------------|---------|------------|
| admin   | ✅ 3.13        | ✅      | ✅ --frozen |
| backend | ✅ 3.13        | ✅      | ✅ --frozen |

## Documentation

- Full policy: `docs/python-dependency-policy.md`
- Admin README: `admin/README.md`
- Backend README: `backend/README.md`
