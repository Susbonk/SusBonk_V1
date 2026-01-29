# Frontend (Svelte + TypeScript)

SusBonk moderator dashboard (Dashboard / Logs / Settings).

## Run (Docker Compose)

From repo root:

```bash
cp .env.example .env
# edit .env and replace CHANGE_ME_* values

docker compose up -d frontend backend
```

Open: `http://localhost:5173`

## Local Development

```bash
npm install
npm run dev
```

## Testing

See `TESTING.md`.

