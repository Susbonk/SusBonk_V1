FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY pyproject.toml .
RUN uv pip install --system fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings python-jose passlib email-validator python-multipart httpx colorama

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
