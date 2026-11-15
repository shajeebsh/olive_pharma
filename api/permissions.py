from rest_framework.permissions import SAFE_METHODS, BasePermission

from core.managers import get_user_role


class IsRepresentativeOrAdmin(BasePermission):
    """Allow representatives and admins (staff are excluded)."""

    message = "Only representatives and admins may use this endpoint."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_user_role(request.user) in {"rep", "admin"}


class IsAdmin(BasePermission):
    message = "Only admins may use this endpoint."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_user_role(request.user) == "admin"


class ReadOnly(BasePermission):
    """Reject any write method; used by the read-only sales list."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
