#!/bin/sh

# Wait until Postgres is ready
POSTGRES_PORT=5432
POSTGRES_HOST=pg-database
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do sleep 1; done

# Set the python path
export PYTHONPATH=$(pwd)

# Run migrations
uv run manage.py migrate

# Run the app
exec uv run manage.py runserver 0.0.0.0:5000 --noreload
