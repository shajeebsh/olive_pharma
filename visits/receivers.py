from django.dispatch import receiver

from .signals import chemist_visit_logged, doctor_visit_logged


@receiver(doctor_visit_logged, dispatch_uid="visits.audit_doctor_visit_logged")
def audit_doctor_visit_logged(sender, visit, rep, **kwargs):
    from core.models import AuditLog

    AuditLog.objects.create(
        user=rep,
        action="doctor_visit_logged",
        object_type="DoctorVisit",
        object_id=str(visit.pk),
        changes={"date": str(visit.date), "doctor_id": visit.doctor_id},
    )


@receiver(chemist_visit_logged, dispatch_uid="visits.audit_chemist_visit_logged")
def audit_chemist_visit_logged(sender, visit, rep, **kwargs):
    from core.models import AuditLog

    AuditLog.objects.create(
        user=rep,
        action="chemist_visit_logged",
        object_type="ChemistVisit",
        object_id=str(visit.pk),
        changes={"date": str(visit.date), "pharmacy_id": visit.pharmacy_id},
    )
