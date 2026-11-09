from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from core.models import AuditLog, Doctor, Hospital, Pharmacy, Product, Region

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

    def test_future_doctor_visit_is_rejected_for_rep(self):
        self.client.force_login(self.rep)
        future = (timezone.localdate() + timedelta(days=1)).isoformat()
        response = self.client.post(
            reverse("visits:doctor_create"),
            {
                "date": future,
                "region": self.region.pk,
                "hospital": self.hospital.pk,
                "doctor": self.doctor.pk,
                "notes": "Future",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be in the future")
        self.assertEqual(DoctorVisit.objects.count(), 0)

    def test_future_doctor_visit_is_allowed_for_admin(self):
        self.client.force_login(self.admin)
        future = (timezone.localdate() + timedelta(days=1)).isoformat()
        response = self.client.post(
            reverse("visits:doctor_create"),
            {
                "date": future,
                "region": self.region.pk,
                "hospital": self.hospital.pk,
                "doctor": self.doctor.pk,
                "notes": "Admin correction",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(DoctorVisit.objects.count(), 1)


class FilterOptionsTests(TestCase):
    def setUp(self):
        self.region_one = Region.objects.create(name="North")
        self.region_two = Region.objects.create(name="South")
        self.hospital_one = Hospital.objects.create(
            name="North Hospital", region=self.region_one
        )
        self.hospital_two = Hospital.objects.create(
            name="South Hospital", region=self.region_two
        )
        self.doctor_one = Doctor.objects.create(
            name="Chen", hospital=self.hospital_one
        )
        self.doctor_two = Doctor.objects.create(
            name="Patel", hospital=self.hospital_two
        )
        self.pharmacy_one = Pharmacy.objects.create(
            name="North Pharmacy",
            region=self.region_one,
            hospital=self.hospital_one,
        )
        self.pharmacy_two = Pharmacy.objects.create(
            name="South Pharmacy",
            region=self.region_two,
            hospital=self.hospital_two,
        )
        self.rep = make_user("rep", ROLE_REP)
        self.client.force_login(self.rep)

    def results(self, **params):
        response = self.client.get(reverse("visits:filter_options"), params)
        self.assertEqual(response.status_code, 200)
        return response.json()["results"]

    def test_hospitals_are_filtered_by_region(self):
        results = self.results(type="hospital", region=self.region_one.pk)
        self.assertEqual([row["id"] for row in results], [self.hospital_one.pk])

    def test_doctors_are_filtered_by_hospital(self):
        results = self.results(type="doctor", hospital=self.hospital_one.pk)
        self.assertEqual([row["id"] for row in results], [self.doctor_one.pk])

    def test_pharmacies_are_filtered_by_hospital(self):
        results = self.results(type="pharmacy", hospital=self.hospital_one.pk)
        self.assertEqual([row["id"] for row in results], [self.pharmacy_one.pk])

    def test_unknown_type_returns_bad_request(self):
        response = self.client.get(reverse("visits:filter_options"), {"type": "x"})
        self.assertEqual(response.status_code, 400)
