import os

from django.contrib.auth import get_user_model

from .models import ROLE_ADMIN, UserProfile


def ensure_superuser_from_env():
    """Create or update the admin account from deployment environment variables."""
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()
    if not email or not password:
        return None

    User = get_user_model()
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

    UserProfile.objects.update_or_create(user=user, defaults={"role": ROLE_ADMIN})
    return user
