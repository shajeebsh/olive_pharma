#!/usr/bin/env bash
# Render start script: ensure collected static files exist before serving.
set -o errexit

python manage.py collectstatic --no-input

exec gunicorn config.wsgi:application
