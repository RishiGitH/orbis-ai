#!/bin/sh

# Wait for the database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate

python manage.py collectstatic --no-input

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn orbis_ai.wsgi:application --bind 0.0.0.0:8000