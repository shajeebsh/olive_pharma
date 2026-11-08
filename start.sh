#!/usr/bin/env bash
# Render start script: ensure migrations and collected static files exist before serving.
set -o errexit

python manage.py migrate --no-input
python manage.py collectstatic --no-input

exec gunicorn config.wsgi:application
