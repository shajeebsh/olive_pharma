from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from core.models import AuditLog, Doctor, Hospital, Product, Region

from .models import DoctorVisit
from .services import log_doctor_visit


def make_user(username, role):
    user = get_user_model().objects.create_user(
        username=username, password="password123"
    )
    user.profile.role = role
    user.profile.save()
    return user


class DoctorVisitServiceTests(TestCase):
    def setUp(self):
        self.rep = make_user("rep", ROLE_REP)
        self.region = Region.objects.create(name="North")
        self.hospital = Hospital.objects.create(name="City", region=self.region)
        self.doctor = Doctor.objects.create(name="Chen", hospital=self.hospital)
        self.product = Product.objects.create(name="Cardiolex", sku="CARD-10")

    def test_log_doctor_visit_creates_products_and_audit(self):
        visit = log_doctor_visit(
            rep=self.rep,
            data={
                "date": "2026-01-10",
                "region": self.region,
                "hospital": self.hospital,
                "doctor": self.doctor,
                "products_introduced": [self.product],
                "notes": "Intro",
            },
        )
        self.assertEqual(visit.rep, self.rep)
        self.assertEqual(list(visit.products_introduced.all()), [self.product])
        audit = AuditLog.objects.get(action="doctor_visit_logged")
        self.assertEqual(audit.object_id, str(visit.pk))


class DoctorVisitAccessTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="North")
        self.hospital = Hospital.objects.create(name="City", region=self.region)
        self.doctor = Doctor.objects.create(name="Chen", hospital=self.hospital)
        self.rep = make_user("rep", ROLE_REP)
        self.staff = make_user("staff", ROLE_STAFF)
        self.admin = make_user("admin", ROLE_ADMIN)

    def test_rep_can_create_doctor_visit(self):
        self.client.force_login(self.rep)
        response = self.client.post(
            reverse("visits:doctor_create"),
            {
                "date": "2026-01-10",
                "region": self.region.pk,
                "hospital": self.hospital.pk,
                "doctor": self.doctor.pk,
                "notes": "Intro",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(DoctorVisit.objects.count(), 1)
        self.assertEqual(DoctorVisit.objects.first().rep, self.rep)

    def test_staff_is_forbidden(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("visits:doctor_list"))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("visits:doctor_list"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_is_redirected(self):
        response = self.client.get(reverse("visits:doctor_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
