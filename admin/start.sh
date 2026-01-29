#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python manage.py dbshell --command="SELECT 1" > /dev/null 2>&1; do
  sleep 1
done

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Creating superuser if not exists..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@susbonk.local')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser created: {username}')
else:
    print('Superuser already exists')
" || true

echo "Starting Django server on port 8090..."
# Use WSGI by default (runserver for development)
# For production ASGI, use: uvicorn db_admin.asgi:application --host 0.0.0.0 --port 8090
python manage.py runserver 0.0.0.0:8090
