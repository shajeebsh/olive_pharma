from django.conf import settings
from django.db import models

from core.models import TimeStampedModel

ROLE_ADMIN = "admin"
ROLE_REP = "rep"
ROLE_STAFF = "staff"

ROLE_CHOICES = [
    (ROLE_ADMIN, "Admin"),
    (ROLE_REP, "Representative"),
    (ROLE_STAFF, "Staff"),
]


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_REP)
    phone = models.CharField(max_length=40, blank=True)
    employee_code = models.CharField(max_length=40, blank=True)
    region = models.ForeignKey(
        "core.Region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
    )

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def is_representative(self):
        return self.role == ROLE_REP

    @property
    def is_staff_member(self):
        return self.role == ROLE_STAFF
