# Frontend Testing Guide

The frontend can be used in two modes:

## 1) Full-stack mode (recommended)

Run backend + DB + Redis, then use real registration/login.

```bash
cp .env.example .env
# edit .env and replace CHANGE_ME_* values

docker compose up -d postgres redis backend frontend
```

Open `http://localhost:5173` and:

1. Register a new user
2. Log in
3. Navigate tabs (Dashboard / Logs / Settings)

## 2) UI-only demo mode

The app supports a UI-only dev shortcut:

- Open `http://localhost:5173/?dev=true`

This bypasses auth and loads a hardcoded demo state for UI testing.

Note: this is gated behind `import.meta.env.DEV` and should only be used with the Vite dev server (`npm run dev`), not production builds.
