from .base import *  # noqa: F401,F403

DEBUG = False

# Serve static files through WhiteNoise's finders as well as STATIC_ROOT. This keeps
# the app working if collectstatic output is missing or a manifest entry is absent.
WHITENOISE_USE_FINDERS = True
STORAGES = {
    **STORAGES,  # noqa: F405
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Render terminates TLS and forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
