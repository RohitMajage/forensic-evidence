#!/bin/bash
set -e

echo "Creating media directories..."
mkdir -p media/evidence media/faces media/voices media/matches

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 120 myproject.wsgi:application
