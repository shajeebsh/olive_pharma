from django.conf import settings
from django.db import models

from core.managers import ScopedManager
from core.models import Doctor, Hospital, Pharmacy, Product, Region, TimeStampedModel


class DoctorVisit(TimeStampedModel):
    rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_visits",
    )
    date = models.DateField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="doctor_visits")
    hospital = models.ForeignKey(
        Hospital, on_delete=models.PROTECT, related_name="doctor_visits"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.PROTECT, related_name="doctor_visits"
    )
    products_introduced = models.ManyToManyField(
        Product, related_name="doctor_visits", blank=True
    )
    notes = models.TextField(blank=True)

    objects = ScopedManager()

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["rep", "date"]),
            models.Index(fields=["hospital", "date"]),
        ]

    def __str__(self):
        return f"{self.rep} -> {self.doctor} on {self.date}"


class ChemistVisit(TimeStampedModel):
    rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chemist_visits",
    )
    date = models.DateField()
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="chemist_visits")
    hospital = models.ForeignKey(
        Hospital, on_delete=models.PROTECT, related_name="chemist_visits"
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name="chemist_visits",
        help_text="Doctor whose locality is being covered.",
    )
    pharmacy = models.ForeignKey(
        Pharmacy, on_delete=models.PROTECT, related_name="chemist_visits"
    )
    current_products = models.TextField(blank=True)
    products_needed = models.ManyToManyField(
        Product, related_name="chemist_visits_needed", blank=True
    )
    notes = models.TextField(blank=True)

    objects = ScopedManager()

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["rep", "date"]),
            models.Index(fields=["hospital", "date"]),
            models.Index(fields=["pharmacy", "date"]),
        ]

    def __str__(self):
        return f"{self.rep} -> {self.pharmacy} on {self.date}"
