from django.conf import settings
from django.db import models
from django.db.models import Q

from core.managers import ScopedManager
from core.models import Doctor, Hospital, Pharmacy, Product, Region, TimeStampedModel


class SalesLog(TimeStampedModel):
    rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sales_logs",
    )
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_entered",
    )
    sales_date = models.DateField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="sales_logs")
    hospital = models.ForeignKey(
        Hospital, on_delete=models.PROTECT, related_name="sales_logs"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.PROTECT, related_name="sales_logs"
    )
    pharmacy = models.ForeignKey(
        Pharmacy, on_delete=models.PROTECT, related_name="sales_logs"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="sales_logs"
    )
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    objects = ScopedManager()

    class Meta:
        ordering = ["-sales_date", "-id"]
        indexes = [
            models.Index(fields=["rep", "sales_date"]),
            models.Index(fields=["hospital", "sales_date"]),
            models.Index(fields=["pharmacy", "sales_date"]),
            models.Index(fields=["product", "sales_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["rep", "reference"],
                condition=~Q(reference=""),
                name="unique_sales_reference_per_rep",
            )
        ]

    def __str__(self):
        return f"{self.rep} {self.product} x{self.quantity} on {self.sales_date}"


class Target(TimeStampedModel):
    PERIOD_MONTH = "month"
    PERIOD_QUARTER = "quarter"
    PERIOD_CHOICES = (
        (PERIOD_MONTH, "Month"),
        (PERIOD_QUARTER, "Quarter"),
    )

    rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="targets",
    )
    period = models.CharField(
        max_length=20, choices=PERIOD_CHOICES, default=PERIOD_MONTH
    )
    start_date = models.DateField()
    end_date = models.DateField()
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="targets",
        help_text="Leave blank for an overall target.",
    )
    amount_target = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    quantity_target = models.PositiveIntegerField(default=0)

    objects = ScopedManager()

    class Meta:
        ordering = ["-start_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["rep", "product", "start_date", "end_date"],
                name="unique_target_per_rep_product_period",
            )
        ]

    def __str__(self):
        return f"{self.rep} {self.start_date}-{self.end_date} target"
