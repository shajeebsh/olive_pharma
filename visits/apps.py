from django.apps import AppConfig


class VisitsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "visits"
    verbose_name = "Doctor & Chemist Visits"

    def ready(self):
        from . import receivers, signals  # noqa: F401
