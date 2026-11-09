from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["object_type", "object_id"])]

    def __str__(self):
        return f"{self.action} {self.object_type}:{self.object_id}"


class Region(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=120, default="Kerala")
    country = models.CharField(max_length=120, default="India")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        location = ", ".join(
            part for part in (self.state, self.country) if part
        )
        return f"{self.name} ({location})" if location else self.name


class Hospital(TimeStampedModel):
    name = models.CharField(max_length=200)
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT, related_name="hospitals"
    )
    city = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["region", "name"])]

    def __str__(self):
        return self.name


class Doctor(TimeStampedModel):
    name = models.CharField(max_length=200)
    hospital = models.ForeignKey(
        Hospital, on_delete=models.PROTECT, related_name="doctors"
    )
    speciality = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["hospital", "name"])]

    def __str__(self):
        return f"Dr. {self.name}"


class Pharmacy(TimeStampedModel):
    name = models.CharField(max_length=200)
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT, related_name="pharmacies"
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pharmacies",
    )
    locality = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["region", "name"])]

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=60, unique=True)
    form = models.CharField(max_length=80, blank=True)
    strength = models.CharField(max_length=80, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"
