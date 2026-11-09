from django.apps import apps
from django.db.models import DateTimeField, Max

PROJECT_APP_LABELS = {
    "accounts",
    "checkin",
    "cms",
    "core",
    "dashboard",
    "sales",
    "visits",
}

TIMESTAMP_FIELDS = ("updated_at", "created_at")


def _latest_field(model):
    meta = model._meta
    for name in TIMESTAMP_FIELDS:
        try:
            field = meta.get_field(name)
        except Exception:
            continue
        if isinstance(field, DateTimeField):
            return field
    for field in meta.concrete_fields:
        if isinstance(field, DateTimeField):
            return field
    return None


def get_table_stats():
    stats = []
    for model in apps.get_models():
        meta = model._meta
        if meta.app_label not in PROJECT_APP_LABELS:
            continue
        if meta.proxy or meta.auto_created:
            continue

        try:
            count = model._default_manager.count()
        except Exception:
            count = None

        latest = None
        field = _latest_field(model)
        if field is not None:
            try:
                latest = model._default_manager.aggregate(value=Max(field.name))["value"]
            except Exception:
                latest = None

        stats.append(
            {
                "app_label": meta.app_label,
                "app_name": meta.app_config.verbose_name,
                "model_name": meta.model_name,
                "model_verbose_name": str(meta.verbose_name),
                "table": meta.db_table,
                "count": count,
                "latest": latest,
                "latest_field": field.name if field is not None else "",
            }
        )

    stats.sort(key=lambda row: (row["app_label"], row["model_name"]))
    return stats
