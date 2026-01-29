FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./

# Additional fixing installation for Postgres, needed to work with db with Linux system
RUN apt-get update && apt-get install -y libpq-dev curl && rm -rf /var/lib/apt/lists/*

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

COPY . /app

CMD ["uv", "run", "main.py"]
