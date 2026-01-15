#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python manage.py dbshell --command="SELECT 1" > /dev/null 2>&1; do
  sleep 1
done

echo "Running migrations..."
# Use --fake-initial for core app since tables already exist from schema.sql
python manage.py migrate --fake-initial

echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
" || true

echo "Starting Django server on port 5000..."
python manage.py runserver 0.0.0.0:5000
