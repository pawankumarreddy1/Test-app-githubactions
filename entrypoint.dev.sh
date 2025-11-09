#!/bin/bash
set -e  # Exit immediately if a command fails


echo "Postgres is up - running migrations"
poetry run python -m core.manage migrate --noinput

echo "Starting project"
exec poetry run python -m core.manage runserver 0.0.0.0:8000
