from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import CheckInOut


def check_in(*, user, date=None, check_in_time=None, notes=""):
    date = date or timezone.localdate()
    check_in_time = check_in_time or timezone.localtime().time()
    if CheckInOut.objects.filter(user=user, date=date).exists():
        raise ValidationError("You have already checked in for this date.")
    return CheckInOut.objects.create(
        user=user, date=date, check_in=check_in_time, notes=notes
    )


def check_out(*, user, date=None, check_out_time=None, notes=""):
    date = date or timezone.localdate()
    record = CheckInOut.objects.filter(user=user, date=date).first()
    if record is None:
        raise ValidationError("No check-in found for this date.")
    if record.check_out is not None:
        raise ValidationError("You have already checked out for this date.")
    record.check_out = check_out_time or timezone.localtime().time()
    if notes:
        record.notes = f"{record.notes}\n{notes}".strip()
    record.save(update_fields=["check_out", "notes", "updated_at"])
    return record
