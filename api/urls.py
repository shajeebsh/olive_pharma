from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

app_name = "api"

urlpatterns = [
    # Auth
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Profile
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # Dashboard
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    # Dependent filter options
    path("filter-options/", views.FilterOptionsView.as_view(), name="filter_options"),
    # Field activity
    path("doctor-visits/", views.DoctorVisitListCreateView.as_view(), name="doctor_visits"),
    path("chemist-visits/", views.ChemistVisitListCreateView.as_view(), name="chemist_visits"),
    # Sales (read-only, own)
    path("sales/", views.SalesLogListView.as_view(), name="sales"),
    # Attendance
    path("checkins/", views.CheckInListView.as_view(), name="checkins"),
    path("checkins/check-in/", views.CheckInCreateView.as_view(), name="check_in"),
    path("checkins/check-out/", views.CheckOutCreateView.as_view(), name="check_out"),
    # Masters
    path("masters/regions/", views.RegionListView.as_view(), name="regions"),
    path("masters/hospitals/", views.HospitalListView.as_view(), name="hospitals"),
    path("masters/doctors/", views.DoctorListView.as_view(), name="doctors"),
    path("masters/pharmacies/", views.PharmacyListView.as_view(), name="pharmacies"),
    path("masters/products/", views.ProductListView.as_view(), name="products"),
]
