from django.http import HttpResponseForbidden

from .managers import get_user_role

EXEMPT_PREFIXES = (
    "/health/",
    "/accounts/",
    "/admin/",
    "/django-admin/",
    "/static/",
    "/media/",
    "/help/",
    "/favicon",
)

ROLE_PATHS = (
    ("/sales/new/", {"admin", "staff"}),
    ("/sales/", {"admin", "staff", "rep"}),
    ("/products/", {"admin"}),
    ("/visits/", {"admin", "rep"}),
    ("/checkin/", {"admin", "rep", "staff"}),
)


class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_exempt(request.path):
            return self.get_response(request)

        if request.user.is_authenticated:
            role = get_user_role(request.user)
            allowed = self._allowed_roles(request.path)
            if allowed is not None and role not in allowed:
                return HttpResponseForbidden(
                    "You do not have permission to access this page."
                )

        return self.get_response(request)

    def _is_exempt(self, path):
        return any(path.startswith(prefix) for prefix in EXEMPT_PREFIXES)

    def _allowed_roles(self, path):
        for prefix, roles in ROLE_PATHS:
            if path.startswith(prefix):
                return roles
        return None
