from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="home"),
    path("reports/", views.ReportsView.as_view(), name="reports"),
    path("reports/export/", views.CSVExportView.as_view(), name="export"),
]
