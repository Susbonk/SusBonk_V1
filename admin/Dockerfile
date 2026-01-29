FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./

# Additional fixing installation for Postgres, needed to work with db with Linux system
RUN apt-get update && apt-get install -y libpq-dev

RUN apt-get update && apt-get install -y netcat-openbsd

RUN uv sync --all-groups

ENV PATH="/app/.venv/bin:$PATH"

COPY . /app

RUN chmod +x ./start.sh
