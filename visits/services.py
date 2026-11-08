from .models import ChemistVisit, DoctorVisit
from .signals import chemist_visit_logged, doctor_visit_logged


def log_doctor_visit(*, rep, data):
    data = dict(data)
    products = data.pop("products_introduced", [])
    visit = DoctorVisit.objects.create(rep=rep, **data)
    visit.products_introduced.set(products)
    doctor_visit_logged.send(sender=DoctorVisit, visit=visit, rep=rep)
    return visit


def log_chemist_visit(*, rep, data):
    data = dict(data)
    products = data.pop("products_needed", [])
    visit = ChemistVisit.objects.create(rep=rep, **data)
    visit.products_needed.set(products)
    chemist_visit_logged.send(sender=ChemistVisit, visit=visit, rep=rep)
    return visit
