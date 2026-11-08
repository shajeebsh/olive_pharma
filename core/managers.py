from django.db import models


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return "admin"
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", None)


class ScopedQuerySet(models.QuerySet):
    def for_user(self, user, owner_field="rep", staff_company_wide=True):
        role = get_user_role(user)
        if user.is_superuser or role == "admin":
            return self
        if role == "staff" and staff_company_wide:
            return self
        return self.filter(**{owner_field: user})


class ScopedManager(models.Manager.from_queryset(ScopedQuerySet)):
    pass
