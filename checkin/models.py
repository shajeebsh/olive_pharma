from django.conf import settings
from django.db import models

from core.managers import ScopedManager
from core.models import TimeStampedModel


class CheckInOut(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="checkins",
    )
    date = models.DateField()
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    objects = ScopedManager()

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [models.Index(fields=["user", "date"])]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"], name="unique_checkin_per_user_per_day"
            )
        ]

    @property
    def is_open(self):
        return self.check_out is None

    @property
    def duration(self):
        if self.check_out is None:
            return None
        from datetime import datetime, timedelta

        start = datetime.combine(self.date, self.check_in)
        end = datetime.combine(self.date, self.check_out)
        if end < start:
            end += timedelta(days=1)
        return end - start

    def __str__(self):
        return f"{self.user} {self.date} {self.check_in}-{self.check_out or '...'}"
