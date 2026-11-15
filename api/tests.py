from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from checkin.models import CheckInOut
from core.models import Doctor, Hospital, Pharmacy, Product, Region
from sales.models import SalesLog
from visits.models import ChemistVisit, DoctorVisit


def make_user(username, role):
    user = get_user_model().objects.create_user(
        username=username, password="password123"
    )
    user.profile.role = role
    user.profile.save()
    return user


class BaseAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.region = Region.objects.create(name="Ernakulam")
        self.hospital = Hospital.objects.create(name="City", region=self.region)
        self.doctor = Doctor.objects.create(name="Chen", hospital=self.hospital)
        self.pharmacy = Pharmacy.objects.create(
            name="Olive", region=self.region, hospital=self.hospital
        )
        self.product = Product.objects.create(name="Cardiolex", sku="CARD-10")
        self.rep = make_user("rep", ROLE_REP)
        self.staff = make_user("staff", ROLE_STAFF)
        self.admin = make_user("admin", ROLE_ADMIN)


class AuthTests(BaseAPITestCase):
    def test_login_returns_tokens_and_user(self):
        response = self.client.post(
            reverse("api:login"),
            {"username": "rep", "password": "password123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["role"], ROLE_REP)

    def test_login_rejects_bad_credentials(self):
        response = self.client.post(
            reverse("api:login"),
            {"username": "rep", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_anonymous_is_denied(self):
        response = self.client.get(reverse("api:doctor_visits"))
        self.assertEqual(response.status_code, 401)


class ProfileTests(BaseAPITestCase):
    def test_get_own_profile(self):
        self.client.force_authenticate(self.rep)
        response = self.client.get(reverse("api:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], ROLE_REP)

    def test_update_phone_and_region(self):
        self.client.force_authenticate(self.rep)
        response = self.client.patch(
            reverse("api:profile"),
            {"phone": "9999999999", "region": self.region.pk},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.rep.profile.refresh_from_db()
        self.assertEqual(self.rep.profile.phone, "9999999999")
        self.assertEqual(self.rep.profile.region_id, self.region.pk)

    def test_role_is_read_only(self):
        self.client.force_authenticate(self.rep)
        self.client.patch(
            reverse("api:profile"), {"role": ROLE_ADMIN}, format="json"
        )
        self.rep.profile.refresh_from_db()
        self.assertEqual(self.rep.profile.role, ROLE_REP)


class DoctorVisitAPITests(BaseAPITestCase):
    def test_rep_creates_visit_with_products(self):
        self.client.force_authenticate(self.rep)
        response = self.client.post(
            reverse("api:doctor_visits"),
            {
                "date": "2026-01-10",
                "region": self.region.pk,
                "hospital": self.hospital.pk,
                "doctor": self.doctor.pk,
                "products_introduced": [self.product.pk],
                "notes": "Intro",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        visit = DoctorVisit.objects.get()
        self.assertEqual(visit.rep, self.rep)
        self.assertEqual(list(visit.products_introduced.all()), [self.product])
        self.assertEqual(response.data["doctor_name"], "Chen")
        self.assertEqual(len(response.data["products_introduced_detail"]), 1)

    def test_future_date_rejected_for_rep(self):
        self.client.force_authenticate(self.rep)
        future = (timezone.localdate() + timedelta(days=1)).isoformat()
        response = self.client.post(
            reverse("api:doctor_visits"),
            {
                "date": future,
                "region": self.region.pk,
                "hospital": self.hospital.pk,
                "doctor": self.doctor.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(DoctorVisit.objects.count(), 0)

    def test_future_date_allowed_for_admin(self):
        self.client.force_authenticate(self.admin)
        future = (timezone.localdate() + timedelta(days=1)).isoformat()
        response = self.client.post(
            reverse("api:doctor_visits"),
            {
                "date": future,
                "region": self.region.pk,
                "hospital": self.hospital.pk,
                "doctor": self.doctor.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_rep_only_sees_own_visits(self):
        other = make_user("rep2", ROLE_REP)
        DoctorVisit.objects.create(
            rep=self.rep, date="2026-01-10", region=self.region,
            hospital=self.hospital, doctor=self.doctor,
        )
        DoctorVisit.objects.create(
            rep=other, date="2026-01-10", region=self.region,
            hospital=self.hospital, doctor=self.doctor,
        )
        self.client.force_authenticate(self.rep)
        response = self.client.get(reverse("api:doctor_visits"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_staff_is_forbidden(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(reverse("api:doctor_visits"))
        self.assertEqual(response.status_code, 403)


class ChemistVisitAPITests(BaseAPITestCase):
    def test_rep_creates_chemist_visit(self):
        self.client.force_authenticate(self.rep)
        response = self.client.post(
            reverse("api:chemist_visits"),
            {
                "date": "2026-01-10",
                "region": self.region.pk,
                "hospital": self.hospital.pk,
                "doctor": self.doctor.pk,
                "pharmacy": self.pharmacy.pk,
                "current_products": "Cardiolex",
                "products_needed": [self.product.pk],
                "quantity": 25,
                "notes": "Restock",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        visit = ChemistVisit.objects.get()
        self.assertEqual(visit.quantity, 25)
        self.assertEqual(list(visit.products_needed.all()), [self.product])


class SalesAPITests(BaseAPITestCase):
    def _sale(self, rep):
        return SalesLog.objects.create(
            rep=rep,
            sales_date="2026-01-10",
            region=self.region,
            hospital=self.hospital,
            doctor=self.doctor,
            pharmacy=self.pharmacy,
            product=self.product,
            quantity=3,
            amount="150.00",
        )

    def test_rep_sees_only_own_sales(self):
        other = make_user("rep2", ROLE_REP)
        self._sale(self.rep)
        self._sale(other)
        self.client.force_authenticate(self.rep)
        response = self.client.get(reverse("api:sales"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_staff_sees_company_wide_sales(self):
        other = make_user("rep2", ROLE_REP)
        self._sale(self.rep)
        self._sale(other)
        self.client.force_authenticate(self.staff)
        response = self.client.get(reverse("api:sales"))
        self.assertEqual(response.data["count"], 2)

    def test_sales_list_is_read_only(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse("api:sales"), {}, format="json")
        self.assertEqual(response.status_code, 405)


class CheckInAPITests(BaseAPITestCase):
    def test_check_in_then_check_out(self):
        self.client.force_authenticate(self.rep)
        response = self.client.post(
            reverse("api:check_in"),
            {"date": "2026-01-10", "check_in": "09:00", "notes": "On time"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_open"])

        response = self.client.post(
            reverse("api:check_out"),
            {"date": "2026-01-10", "check_out": "17:30", "notes": "Done"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_open"])
        self.assertEqual(response.data["duration"], "8:30:00")
        self.assertIn("Done", response.data["notes"])

    def test_duplicate_check_in_rejected(self):
        self.client.force_authenticate(self.rep)
        self.client.post(
            reverse("api:check_in"),
            {"date": "2026-01-10", "check_in": "09:00"},
            format="json",
        )
        response = self.client.post(
            reverse("api:check_in"),
            {"date": "2026-01-10", "check_in": "09:30"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CheckInOut.objects.count(), 1)

    def test_check_out_without_check_in_rejected(self):
        self.client.force_authenticate(self.rep)
        response = self.client.post(
            reverse("api:check_out"),
            {"date": "2026-01-10", "check_out": "17:30"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_list_only_own_records(self):
        other = make_user("rep2", ROLE_REP)
        CheckInOut.objects.create(user=self.rep, date="2026-01-10", check_in="09:00")
        CheckInOut.objects.create(user=other, date="2026-01-10", check_in="09:00")
        self.client.force_authenticate(self.rep)
        response = self.client.get(reverse("api:checkins"))
        self.assertEqual(response.data["count"], 1)


class FilterOptionsAPITests(BaseAPITestCase):
    def test_hospitals_by_region(self):
        self.client.force_authenticate(self.rep)
        response = self.client.get(
            reverse("api:filter_options"), {"type": "hospital", "region": self.region.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([r["id"] for r in response.data["results"]], [self.hospital.pk])

    def test_pharmacies_by_hospital(self):
        self.client.force_authenticate(self.rep)
        response = self.client.get(
            reverse("api:filter_options"),
            {"type": "pharmacy", "hospital": self.hospital.pk},
        )
        self.assertEqual([r["id"] for r in response.data["results"]], [self.pharmacy.pk])

    def test_unknown_type_is_bad_request(self):
        self.client.force_authenticate(self.rep)
        response = self.client.get(reverse("api:filter_options"), {"type": "x"})
        self.assertEqual(response.status_code, 400)


class MastersAPITests(BaseAPITestCase):
    def test_lists_are_available(self):
        self.client.force_authenticate(self.rep)
        for name in ("regions", "hospitals", "doctors", "pharmacies", "products"):
            response = self.client.get(reverse(f"api:{name}"))
            self.assertEqual(response.status_code, 200, name)

    def test_products_filter_by_active(self):
        Product.objects.create(name="Old", sku="OLD-1", active=False)
        self.client.force_authenticate(self.rep)
        response = self.client.get(reverse("api:products"), {"active": "true"})
        self.assertEqual(response.data["count"], 1)


class DashboardAPITests(BaseAPITestCase):
    def test_dashboard_returns_kpis_and_recent(self):
        DoctorVisit.objects.create(
            rep=self.rep, date=timezone.localdate(), region=self.region,
            hospital=self.hospital, doctor=self.doctor,
        )
        self.client.force_authenticate(self.rep)
        response = self.client.get(reverse("api:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["kpis"]["doctor_visits"], 1)
        self.assertEqual(len(response.data["recent_visits"]), 1)
