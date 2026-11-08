NAV_REGISTRY = {
    "admin": [
        {"label": "Dashboard", "url_name": "dashboard:home", "icon": "bi-speedometer2"},
        {"label": "Reports", "url_name": "dashboard:reports", "icon": "bi-bar-chart"},
        {"label": "Meet Doctor", "url_name": "visits:doctor_list", "icon": "bi-person-badge"},
        {"label": "Meet Chemist", "url_name": "visits:chemist_list", "icon": "bi-capsule"},
        {"label": "Sales", "url_name": "sales:list", "icon": "bi-cash-stack"},
        {"label": "Check In/Out", "url_name": "checkin:list", "icon": "bi-clock"},
        {"label": "Help", "url_name": "help", "icon": "bi-question-circle"},
    ],
    "rep": [
        {"label": "Dashboard", "url_name": "dashboard:home", "icon": "bi-speedometer2"},
        {"label": "Reports", "url_name": "dashboard:reports", "icon": "bi-bar-chart"},
        {"label": "Meet Doctor", "url_name": "visits:doctor_list", "icon": "bi-person-badge"},
        {"label": "Meet Chemist", "url_name": "visits:chemist_list", "icon": "bi-capsule"},
        {"label": "Check In/Out", "url_name": "checkin:list", "icon": "bi-clock"},
    ],
    "staff": [
        {"label": "Dashboard", "url_name": "dashboard:home", "icon": "bi-speedometer2"},
        {"label": "Reports", "url_name": "dashboard:reports", "icon": "bi-bar-chart"},
        {"label": "Sales", "url_name": "sales:list", "icon": "bi-cash-stack"},
        {"label": "Check In/Out", "url_name": "checkin:list", "icon": "bi-clock"},
    ],
}


def nav_for_role(role):
    return NAV_REGISTRY.get(role, [])
