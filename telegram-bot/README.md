# Telegram Bot

Telegram group integration + message handling for SusBonk.

## Run (Docker Compose)

From repo root:

```bash
cp .env.example .env
# edit .env and replace CHANGE_ME_* values (especially TELEGRAM_BOT_TOKEN)

docker compose up -d postgres redis backend telegram-bot
```

## Generate database entities

Requires [sea-orm-cli](https://www.sea-ql.org/SeaORM/docs/generate-entity/sea-orm-cli/)

```sh
chmod u+x ./scripts/generate_entities.sh

./scripts/generate_entities.sh
```
