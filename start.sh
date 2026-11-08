#!/usr/bin/env sh
# Render start command: migrate, superuser, collectstatic, serve via gunicorn
set -e

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

python manage.py migrate --no-input
python manage.py ensure_superuser
python manage.py collectstatic --no-input

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 3 --timeout 120
