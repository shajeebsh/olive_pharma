from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from core.models import Product
from sales.models import SalesLog
from visits.models import ChemistVisit, DoctorVisit

from .services import (
    chemist_visits_queryset,
    doctor_visits_queryset,
    hospital_breakdown,
    rep_breakdown,
    sales_queryset,
)

REPORTS = {
    "monthly": {
        "label": "Monthly",
        "columns": [
            ("period", "Month"),
            ("doctor_visits", "Doctor Visits"),
            ("chemist_visits", "Chemist Visits"),
            ("sales_quantity", "Quantity"),
            ("sales_amount", "Sales Amount"),
        ],
    },
    "representatives": {
        "label": "Representatives",
        "columns": [
            ("rep", "Representative"),
            ("doctor_visits", "Doctor Visits"),
            ("chemist_visits", "Chemist Visits"),
            ("checkins", "Check-ins"),
            ("sales_quantity", "Quantity"),
            ("sales_amount", "Sales Amount"),
        ],
    },
    "hospitals": {
        "label": "Hospitals",
        "columns": [
            ("hospital", "Hospital"),
            ("state", "State"),
            ("country", "Country"),
            ("doctor_visits", "Doctor Visits"),
            ("chemist_visits", "Chemist Visits"),
            ("sales_quantity", "Quantity"),
            ("sales_amount", "Sales Amount"),
        ],
    },
    "products": {
        "label": "Products",
        "columns": [
            ("product", "Product"),
            ("introduced", "Doctors Introduced"),
            ("demanded", "Chemist Demand"),
            ("sales_quantity", "Quantity"),
            ("sales_amount", "Sales Amount"),
        ],
    },
}

REPORT_ORDER = ["monthly", "representatives", "hospitals", "products"]


def monthly_rows(user, filters):
    sales = (
        sales_queryset(user, filters)
        .annotate(month=TruncMonth("sales_date"))
        .values("month")
        .annotate(
            sales_amount=Sum("amount"),
            sales_quantity=Sum("quantity"),
        )
    )
    doctors = (
        doctor_visits_queryset(user, filters)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Count("id"))
    )
    chemists = (
        chemist_visits_queryset(user, filters)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Count("id"))
    )
    doctor_map = {row["month"]: row["total"] for row in doctors}
    chemist_map = {row["month"]: row["total"] for row in chemists}

    merged = {}
    for row in sales:
        merged[row["month"]] = {
            "period": row["month"].strftime("%Y-%m"),
            "sales_amount": row["sales_amount"] or 0,
            "sales_quantity": row["sales_quantity"] or 0,
        }
    for month in set(doctor_map) | set(chemist_map):
        if month not in merged:
            merged[month] = {
                "period": month.strftime("%Y-%m"),
                "sales_amount": 0,
                "sales_quantity": 0,
            }
    for month, row in merged.items():
        row["doctor_visits"] = doctor_map.get(month, 0)
        row["chemist_visits"] = chemist_map.get(month, 0)
    return [merged[key] for key in sorted(merged)]


def product_rows(user, filters):
    sales = (
        sales_queryset(user, filters)
        .values("product_id", "product__name")
        .annotate(sales_amount=Sum("amount"), sales_quantity=Sum("quantity"))
    )
    introduced = (
        DoctorVisit.products_introduced.through.objects.filter(
            doctorvisit__in=doctor_visits_queryset(user, filters)
        )
        .values("product_id")
        .annotate(total=Count("doctorvisit_id", distinct=True))
    )
    demanded = (
        ChemistVisit.products_needed.through.objects.filter(
            chemistvisit__in=chemist_visits_queryset(user, filters)
        )
        .values("product_id")
        .annotate(total=Count("chemistvisit_id", distinct=True))
    )
    introduced_map = {row["product_id"]: row["total"] for row in introduced}
    demanded_map = {row["product_id"]: row["total"] for row in demanded}

    rows = []
    seen = set()
    for row in sales:
        seen.add(row["product_id"])
        rows.append(
            {
                "product_id": row["product_id"],
                "product": row["product__name"],
                "sales_amount": row["sales_amount"] or 0,
                "sales_quantity": row["sales_quantity"] or 0,
                "introduced": introduced_map.get(row["product_id"], 0),
                "demanded": demanded_map.get(row["product_id"], 0),
            }
        )
    extra_ids = (set(introduced_map) | set(demanded_map)) - seen
    if extra_ids:
        names = dict(
            Product.objects.filter(id__in=extra_ids).values_list("id", "name")
        )
        for product_id in extra_ids:
            rows.append(
                {
                    "product_id": product_id,
                    "product": names.get(product_id, "-"),
                    "sales_amount": 0,
                    "sales_quantity": 0,
                    "introduced": introduced_map.get(product_id, 0),
                    "demanded": demanded_map.get(product_id, 0),
                }
            )
    rows.sort(key=lambda r: (r["sales_amount"], r["introduced"]), reverse=True)
    return rows


def get_report_rows(name, user, filters):
    if name == "monthly":
        return monthly_rows(user, filters)
    if name == "representatives":
        return rep_breakdown(user, filters)
    if name == "hospitals":
        return hospital_breakdown(user, filters)
    if name == "products":
        return product_rows(user, filters)
    return []


def chart_data(name, rows):
    if name == "monthly":
        labels = [row["period"] for row in rows]
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Doctor Visits",
                    "data": [row["doctor_visits"] for row in rows],
                },
                {
                    "label": "Chemist Visits",
                    "data": [row["chemist_visits"] for row in rows],
                },
            ],
        }
    if name == "representatives":
        return {
            "labels": [row["rep"] for row in rows],
            "datasets": [
                {
                    "label": "Sales Amount",
                    "data": [float(row["sales_amount"]) for row in rows],
                }
            ],
        }
    if name == "hospitals":
        return {
            "labels": [row["hospital"] for row in rows],
            "datasets": [
                {
                    "label": "Sales Amount",
                    "data": [float(row["sales_amount"]) for row in rows],
                }
            ],
        }
    return {
        "labels": [row["product"] for row in rows],
        "datasets": [
            {
                "label": "Sales Amount",
                "data": [float(row["sales_amount"]) for row in rows],
            }
        ],
    }
