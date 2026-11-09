from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from core.models import AuditLog, Doctor, Hospital, Pharmacy, Product, Region

from .models import SalesLog, Target
from .services import target_attainment


def make_user(username, role):
    user = get_user_model().objects.create_user(
        username=username, password="password123"
    )
    user.profile.role = role
    user.profile.save()
    return user


class SalesTestBase(TestCase):
    def setUp(self):
        self.admin = make_user("admin", ROLE_ADMIN)
        self.staff = make_user("staff", ROLE_STAFF)
        self.rep = make_user("rep", ROLE_REP)
        self.region = Region.objects.create(name="North")
        self.hospital = Hospital.objects.create(name="City", region=self.region)
        self.doctor = Doctor.objects.create(name="Chen", hospital=self.hospital)
        self.pharmacy = Pharmacy.objects.create(name="Olive", region=self.region)
        self.product = Product.objects.create(name="Cardiolex", sku="CARD-10")

    def sales_payload(self, reference="INV-1"):
        return {
            "rep": self.rep.pk,
            "sales_date": "2026-01-10",
            "region": self.region.pk,
            "hospital": self.hospital.pk,
            "doctor": self.doctor.pk,
            "pharmacy": self.pharmacy.pk,
            "product": self.product.pk,
            "quantity": 10,
            "amount": "250.00",
            "reference": reference,
            "notes": "",
        }


class SalesEntryTests(SalesTestBase):
    def test_staff_can_create_sale(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("sales:create"), self.sales_payload())
        self.assertEqual(response.status_code, 302)
        sale = SalesLog.objects.get()
        self.assertEqual(sale.entered_by, self.staff)
        self.assertTrue(AuditLog.objects.filter(action="sales_logged").exists())

    def test_duplicate_reference_is_rejected(self):
        self.client.force_login(self.staff)
        self.client.post(reverse("sales:create"), self.sales_payload())
        response = self.client.post(reverse("sales:create"), self.sales_payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SalesLog.objects.count(), 1)
        self.assertContains(response, "already exists")

    def test_rep_cannot_create_but_can_list(self):
        self.client.force_login(self.rep)
        self.assertEqual(
            self.client.get(reverse("sales:create")).status_code, 403
        )
        self.assertEqual(self.client.get(reverse("sales:list")).status_code, 200)

    def test_future_sale_is_rejected_for_staff(self):
        self.client.force_login(self.staff)
        payload = self.sales_payload()
        payload["sales_date"] = (
            timezone.localdate() + timedelta(days=1)
        ).isoformat()
        response = self.client.post(reverse("sales:create"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be in the future")
        self.assertEqual(SalesLog.objects.count(), 0)

    def test_future_sale_is_allowed_for_admin(self):
        self.client.force_login(self.admin)
        payload = self.sales_payload()
        payload["sales_date"] = (
            timezone.localdate() + timedelta(days=1)
        ).isoformat()
        response = self.client.post(reverse("sales:create"), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SalesLog.objects.count(), 1)


class TargetAttainmentTests(SalesTestBase):
    def test_attainment_calculation(self):
        Target.objects.create(
            rep=self.rep,
            start_date="2026-01-01",
            end_date="2026-01-31",
            amount_target=Decimal("1000.00"),
            quantity_target=40,
        )
        SalesLog.objects.create(
            rep=self.rep,
            entered_by=self.staff,
            sales_date="2026-01-10",
            region=self.region,
            hospital=self.hospital,
            doctor=self.doctor,
            pharmacy=self.pharmacy,
            product=self.product,
            quantity=10,
            amount=Decimal("250.00"),
        )
        result = target_attainment(
            rep=self.rep, start_date="2026-01-01", end_date="2026-01-31"
        )
        self.assertEqual(result["actual_amount"], Decimal("250.00"))
        self.assertEqual(result["amount_attainment"], 25.0)
        self.assertEqual(result["quantity_attainment"], 25.0)
