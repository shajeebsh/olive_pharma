from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

SECRET_KEY = "django-insecure-local-development-key"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Serve plain static files locally without requiring collectstatic.
STORAGES = {
    **STORAGES,  # noqa: F405
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
