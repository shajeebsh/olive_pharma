from django.urls import path

from . import views

app_name = "checkin"

urlpatterns = [
    path("", views.CheckInListView.as_view(), name="list"),
    path("in/", views.CheckInView.as_view(), name="check_in"),
    path("out/", views.CheckOutView.as_view(), name="check_out"),
]
