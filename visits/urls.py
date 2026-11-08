from django.urls import path

from . import views

app_name = "visits"

urlpatterns = [
    path("doctor/", views.DoctorVisitListView.as_view(), name="doctor_list"),
    path("doctor/new/", views.DoctorVisitCreateView.as_view(), name="doctor_create"),
    path("chemist/", views.ChemistVisitListView.as_view(), name="chemist_list"),
    path("chemist/new/", views.ChemistVisitCreateView.as_view(), name="chemist_create"),
]
