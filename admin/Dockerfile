FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock .python-version ./
RUN pip install --no-cache-dir uv && \
    uv sync --frozen

COPY . .

RUN chmod +x start.sh

EXPOSE 8090

CMD ["./start.sh"]
