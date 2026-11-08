from django.db.models import Sum

from .models import SalesLog, Target
from .signals import sales_logged


def log_sales(*, data, entered_by):
    data = dict(data)
    sale = SalesLog.objects.create(entered_by=entered_by, **data)
    sales_logged.send(sender=SalesLog, sale=sale, entered_by=entered_by)
    return sale


def target_attainment(*, rep, start_date, end_date, product=None):
    targets = Target.objects.filter(
        rep=rep, start_date__lte=end_date, end_date__gte=start_date
    )
    sales = SalesLog.objects.filter(
        rep=rep, sales_date__range=(start_date, end_date)
    )
    if product is not None:
        targets = targets.filter(product=product)
        sales = sales.filter(product=product)

    target_totals = targets.aggregate(
        amount=Sum("amount_target"), quantity=Sum("quantity_target")
    )
    actual_totals = sales.aggregate(amount=Sum("amount"), quantity=Sum("quantity"))

    target_amount = target_totals["amount"] or 0
    actual_amount = actual_totals["amount"] or 0
    target_quantity = target_totals["quantity"] or 0
    actual_quantity = actual_totals["quantity"] or 0

    return {
        "target_amount": target_amount,
        "actual_amount": actual_amount,
        "target_quantity": target_quantity,
        "actual_quantity": actual_quantity,
        "amount_attainment": (
            round(actual_amount / target_amount * 100, 1) if target_amount else None
        ),
        "quantity_attainment": (
            round(actual_quantity / target_quantity * 100, 1)
            if target_quantity
            else None
        ),
    }
