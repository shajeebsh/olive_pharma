from .managers import get_user_role
from .navigation import nav_for_role


def navigation(request):
    role = get_user_role(getattr(request, "user", None))
    return {
        "NAV_ITEMS": nav_for_role(role),
        "USER_ROLE": role,
    }
