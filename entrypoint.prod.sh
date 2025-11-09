#!/bin/bash
set -e

echo "Running migrations..."
poetry run python -m core.manage makemigrations --noinput
poetry run python -m core.manage migrate --noinput

echo "Collecting static files..."
poetry run python -m core.manage collectstatic --noinput


echo "Starting Gunicorn server..."
exec poetry run gunicorn core.hostelbackend.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --threads 2 \
    --timeout 120
