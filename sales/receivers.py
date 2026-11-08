from django.dispatch import receiver

from .signals import sales_logged


@receiver(sales_logged, dispatch_uid="sales.audit_sales_logged")
def audit_sales_logged(sender, sale, entered_by, **kwargs):
    from core.models import AuditLog

    AuditLog.objects.create(
        user=entered_by,
        action="sales_logged",
        object_type="SalesLog",
        object_id=str(sale.pk),
        changes={
            "rep_id": sale.rep_id,
            "amount": str(sale.amount),
            "quantity": sale.quantity,
        },
    )
