#!/usr/bin/env sh
# Render start command: migrate, provision superuser, collectstatic, serve via gunicorn
set -e

python manage.py migrate --no-input

python - <<'PY'
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
django.setup()

from django.contrib.auth import get_user_model

from accounts.models import ROLE_ADMIN, UserProfile

User = get_user_model()
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()

if email and password:
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        user = User.objects.filter(username__iexact=email).first()
    if user is None:
        user = User(username=email)

    user.username = email
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()

    UserProfile.objects.update_or_create(
        user=user, defaults={"role": ROLE_ADMIN}
    )
    print(f"Superuser ready: {email}")
elif email or password:
    print("Both DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD are required.")
PY

python manage.py collectstatic --no-input

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 3 --timeout 120
