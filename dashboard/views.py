import csv
import json

from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from core.permissions import RoleRequiredMixin

from .forms import DashboardFilterForm
from .reports import REPORTS, REPORT_ORDER, chart_data, get_report_rows
from .services import hospital_breakdown, kpis, recent_activity, rep_breakdown


def _resolve_filters(request):
    form = DashboardFilterForm(request.GET or None, user=request.user)
    return form, form.as_filters()


class DashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = ("admin", "staff", "rep")
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form, filters = _resolve_filters(self.request)
        reps = rep_breakdown(self.request.user, filters)[:10]
        hospitals = hospital_breakdown(self.request.user, filters)[:10]
        context.update(
            {
                "form": form,
                "filters": filters,
                "kpis": kpis(self.request.user, filters),
                "recent_activity": recent_activity(self.request.user, filters),
                "rep_rows": reps,
                "hospital_rows": hospitals,
                "rep_chart": json.dumps(
                    {
                        "labels": [row["rep"] for row in reps],
                        "datasets": [
                            {
                                "label": "Sales Amount",
                                "data": [float(row["sales_amount"]) for row in reps],
                            }
                        ],
                    }
                ),
                "hospital_chart": json.dumps(
                    {
                        "labels": [row["hospital"] for row in hospitals],
                        "datasets": [
                            {
                                "label": "Sales Amount",
                                "data": [
                                    float(row["sales_amount"]) for row in hospitals
                                ],
                            }
                        ],
                    }
                ),
            }
        )
        return context


class ReportsView(RoleRequiredMixin, TemplateView):
    allowed_roles = ("admin", "staff", "rep")
    template_name = "dashboard/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form, filters = _resolve_filters(self.request)
        tab = self.request.GET.get("tab", "monthly")
        if tab not in REPORTS:
            tab = "monthly"
        rows = get_report_rows(tab, self.request.user, filters)
        context.update(
            {
                "form": form,
                "filters": filters,
                "active_tab": tab,
                "rows": rows,
                "columns": REPORTS[tab]["columns"],
                "tabs": [
                    (key, REPORTS[key]["label"]) for key in REPORT_ORDER
                ],
                "chart": json.dumps(chart_data(tab, rows)),
            }
        )
        return context


class CSVExportView(RoleRequiredMixin, View):
    allowed_roles = ("admin", "staff", "rep")

    def get(self, request, *args, **kwargs):
        _, filters = _resolve_filters(request)
        report = request.GET.get("report", "monthly")
        if report not in REPORTS:
            report = "monthly"

        rows = get_report_rows(report, request.user, filters)
        columns = REPORTS[report]["columns"]

        response = HttpResponse(content_type="text/csv")
        filename = f"{report}-{timezone.localdate():%Y-%m-%d}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([label for _, label in columns])
        for row in rows:
            writer.writerow([row.get(key, "") for key, _ in columns])
        return response
