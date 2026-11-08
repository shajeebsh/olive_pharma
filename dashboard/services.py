from django.db.models import Count, Sum

from checkin.models import CheckInOut
from sales.models import SalesLog
from visits.models import ChemistVisit, DoctorVisit


def sales_queryset(user, filters):
    qs = SalesLog.objects.for_user(user, "rep").filter(
        sales_date__range=(filters["start_date"], filters["end_date"])
    )
    return _narrow(qs, filters)


def doctor_visits_queryset(user, filters):
    qs = DoctorVisit.objects.for_user(user, "rep").filter(
        date__range=(filters["start_date"], filters["end_date"])
    )
    if filters.get("product"):
        qs = qs.filter(products_introduced=filters["product"])
    if filters.get("rep"):
        qs = qs.filter(rep=filters["rep"])
    if filters.get("hospital"):
        qs = qs.filter(hospital=filters["hospital"])
    return qs


def chemist_visits_queryset(user, filters):
    qs = ChemistVisit.objects.for_user(user, "rep").filter(
        date__range=(filters["start_date"], filters["end_date"])
    )
    if filters.get("product"):
        qs = qs.filter(products_needed=filters["product"])
    if filters.get("rep"):
        qs = qs.filter(rep=filters["rep"])
    if filters.get("hospital"):
        qs = qs.filter(hospital=filters["hospital"])
    return qs


def checkins_queryset(user, filters):
    qs = CheckInOut.objects.for_user(user, "user").filter(
        date__range=(filters["start_date"], filters["end_date"])
    )
    if filters.get("rep"):
        qs = qs.filter(user=filters["rep"])
    return qs


def _narrow(qs, filters):
    if filters.get("rep"):
        qs = qs.filter(rep=filters["rep"])
    if filters.get("hospital"):
        qs = qs.filter(hospital=filters["hospital"])
    if filters.get("product"):
        qs = qs.filter(product=filters["product"])
    return qs


def kpis(user, filters):
    sales = sales_queryset(user, filters)
    amount = sales.aggregate(total=Sum("amount"))["total"] or 0
    return {
        "doctor_visits": doctor_visits_queryset(user, filters).count(),
        "chemist_visits": chemist_visits_queryset(user, filters).count(),
        "checkins": checkins_queryset(user, filters).count(),
        "sales_amount": amount,
        "sales_count": sales.count(),
    }


def rep_breakdown(user, filters):
    sales = (
        sales_queryset(user, filters)
        .values("rep_id", "rep__username")
        .annotate(amount=Sum("amount"), quantity=Sum("quantity"))
        .order_by("-amount")
    )
    doctors = (
        doctor_visits_queryset(user, filters)
        .values("rep_id")
        .annotate(total=Count("id"))
    )
    chemists = (
        chemist_visits_queryset(user, filters)
        .values("rep_id")
        .annotate(total=Count("id"))
    )
    checkins = (
        checkins_queryset(user, filters).values("user_id").annotate(total=Count("id"))
    )
    doctor_map = {row["rep_id"]: row["total"] for row in doctors}
    chemist_map = {row["rep_id"]: row["total"] for row in chemists}
    checkin_map = {row["user_id"]: row["total"] for row in checkins}

    rows = []
    seen = set()
    for row in sales:
        seen.add(row["rep_id"])
        rows.append(
            {
                "rep_id": row["rep_id"],
                "rep": row["rep__username"],
                "sales_amount": row["amount"] or 0,
                "sales_quantity": row["quantity"] or 0,
                "doctor_visits": doctor_map.get(row["rep_id"], 0),
                "chemist_visits": chemist_map.get(row["rep_id"], 0),
                "checkins": checkin_map.get(row["rep_id"], 0),
            }
        )
    extra_ids = (set(doctor_map) | set(chemist_map) | set(checkin_map)) - seen
    if extra_ids:
        from django.contrib.auth import get_user_model

        names = dict(
            get_user_model()
            .objects.filter(id__in=extra_ids)
            .values_list("id", "username")
        )
        for rep_id in extra_ids:
            rows.append(
                {
                    "rep_id": rep_id,
                    "rep": names.get(rep_id, "-"),
                    "sales_amount": 0,
                    "sales_quantity": 0,
                    "doctor_visits": doctor_map.get(rep_id, 0),
                    "chemist_visits": chemist_map.get(rep_id, 0),
                    "checkins": checkin_map.get(rep_id, 0),
                }
            )
    rows.sort(key=lambda r: (r["sales_amount"], r["doctor_visits"]), reverse=True)
    return rows


def hospital_breakdown(user, filters):
    sales = (
        sales_queryset(user, filters)
        .values("hospital_id", "hospital__name")
        .annotate(amount=Sum("amount"), quantity=Sum("quantity"))
        .order_by("-amount")
    )
    doctors = (
        doctor_visits_queryset(user, filters)
        .values("hospital_id")
        .annotate(total=Count("id"))
    )
    chemists = (
        chemist_visits_queryset(user, filters)
        .values("hospital_id")
        .annotate(total=Count("id"))
    )
    doctor_map = {row["hospital_id"]: row["total"] for row in doctors}
    chemist_map = {row["hospital_id"]: row["total"] for row in chemists}

    rows = []
    seen = set()
    for row in sales:
        seen.add(row["hospital_id"])
        rows.append(
            {
                "hospital_id": row["hospital_id"],
                "hospital": row["hospital__name"],
                "sales_amount": row["amount"] or 0,
                "sales_quantity": row["quantity"] or 0,
                "doctor_visits": doctor_map.get(row["hospital_id"], 0),
                "chemist_visits": chemist_map.get(row["hospital_id"], 0),
            }
        )
    extra_ids = (set(doctor_map) | set(chemist_map)) - seen
    if extra_ids:
        from core.models import Hospital

        names = dict(
            Hospital.objects.filter(id__in=extra_ids).values_list("id", "name")
        )
        for hospital_id in extra_ids:
            rows.append(
                {
                    "hospital_id": hospital_id,
                    "hospital": names.get(hospital_id, "-"),
                    "sales_amount": 0,
                    "sales_quantity": 0,
                    "doctor_visits": doctor_map.get(hospital_id, 0),
                    "chemist_visits": chemist_map.get(hospital_id, 0),
                }
            )
    rows.sort(key=lambda r: (r["sales_amount"], r["doctor_visits"]), reverse=True)
    return rows


def recent_activity(user, filters, limit=5):
    doctors = (
        doctor_visits_queryset(user, filters)
        .select_related("rep", "doctor", "hospital")
        .order_by("-date", "-id")[:limit]
    )
    chemists = (
        chemist_visits_queryset(user, filters)
        .select_related("rep", "pharmacy", "hospital")
        .order_by("-date", "-id")[:limit]
    )
    items = [{"kind": "doctor", "obj": visit} for visit in doctors]
    items += [{"kind": "chemist", "obj": visit} for visit in chemists]
    items.sort(
        key=lambda item: (item["obj"].date, item["obj"].pk), reverse=True
    )
    return items[:limit]
