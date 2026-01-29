# Admin (Django)

Admin panel for managing SusBonk data in PostgreSQL.

## Run (Docker Compose)

From repo root:

```bash
cp .env.example .env
# edit .env and replace CHANGE_ME_* values

docker compose up -d postgres admin
```

Admin UI:

- `http://localhost:8090/admin`

Credentials come from env vars (see `.env.example`):

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_PASSWORD`
