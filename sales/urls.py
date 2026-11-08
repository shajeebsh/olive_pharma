from django.urls import path

from . import views

app_name = "sales"

urlpatterns = [
    path("", views.SalesLogListView.as_view(), name="list"),
    path("new/", views.SalesLogCreateView.as_view(), name="create"),
    path("targets/", views.TargetListView.as_view(), name="target_list"),
    path("targets/new/", views.TargetCreateView.as_view(), name="target_create"),
]
