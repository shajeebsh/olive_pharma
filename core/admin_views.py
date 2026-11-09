from django.contrib import admin, messages
from django.shortcuts import redirect, render

from .services.profiling import get_table_stats
from .services.seeding import seed_rows, seedable_models


@admin.site.admin_view
def db_profiling_view(request):
    context = {
        **admin.site.each_context(request),
        "title": "DB Profiling",
        "stats": get_table_stats(),
        "seedable_models": seedable_models(),
    }
    return render(request, "admin/core/db_profiling.html", context)


@admin.site.admin_view
def seed_table_view(request):
    if request.method != "POST":
        return redirect("admin_db_profiling")

    label = request.POST.get("model", "")
    try:
        rows = int(request.POST.get("rows", "10"))
    except (TypeError, ValueError):
        rows = 10

    if rows < 1 or rows > 1000:
        messages.error(request, "Rows must be between 1 and 1000.")
        return redirect("admin_db_profiling")

    try:
        created = seed_rows(label, rows)
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Seeded {created} row(s) for {label}.")
    return redirect("admin_db_profiling")
