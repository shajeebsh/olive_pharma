from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from core.models import Doctor, Hospital, Region
from visits.models import DoctorVisit


def make_user(username, role):
    user = get_user_model().objects.create_user(
        username=username, password="password123"
    )
    user.profile.role = role
    user.profile.save()
    return user


class ScopingTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="North")
        self.hospital = Hospital.objects.create(name="City", region=self.region)
        self.doctor = Doctor.objects.create(name="Chen", hospital=self.hospital)
        self.admin = make_user("admin", ROLE_ADMIN)
        self.staff = make_user("staff", ROLE_STAFF)
        self.rep1 = make_user("rep1", ROLE_REP)
        self.rep2 = make_user("rep2", ROLE_REP)

        for rep in (self.rep1, self.rep2):
            DoctorVisit.objects.create(
                rep=rep,
                date="2026-01-10",
                region=self.region,
                hospital=self.hospital,
                doctor=self.doctor,
            )

    def test_rep_sees_only_own_visits(self):
        visits = DoctorVisit.objects.for_user(self.rep1, "rep")
        self.assertEqual(visits.count(), 1)
        self.assertEqual(visits.first().rep, self.rep1)

    def test_admin_and_staff_see_all_visits(self):
        self.assertEqual(DoctorVisit.objects.for_user(self.admin, "rep").count(), 2)
        self.assertEqual(DoctorVisit.objects.for_user(self.staff, "rep").count(), 2)


class HealthTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
