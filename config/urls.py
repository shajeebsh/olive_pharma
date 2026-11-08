"""URL configuration for OlivePharma."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from core import views as core_views

urlpatterns = [
    path("health/", core_views.health, name="health"),
    path("help/", TemplateView.as_view(template_name="help.html"), name="help"),
    path("django-admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", include("accounts.urls")),
    path("visits/", include("visits.urls")),
    path("sales/", include("sales.urls")),
    path("checkin/", include("checkin.urls")),
    path("", include("dashboard.urls")),
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
