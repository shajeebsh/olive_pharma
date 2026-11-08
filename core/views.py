from django.db import connection
from django.http import JsonResponse


def health(request):
    database_ok = False
    migrations_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            database_ok = True
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migrations_ok = cursor.fetchone()[0] > 0
    except Exception:
        pass

    healthy = database_ok and migrations_ok
    return JsonResponse(
        {
            "status": "ok" if healthy else "error",
            "service": "olive_pharma",
            "database": "ok" if database_ok else "error",
            "migrations": "ok" if migrations_ok else "missing",
        },
        status=200 if healthy else 503,
    )
