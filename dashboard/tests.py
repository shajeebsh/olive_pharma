from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from core.models import Doctor, Hospital, Pharmacy, Product, Region
from sales.models import SalesLog


def make_user(username, role):
    user = get_user_model().objects.create_user(
        username=username, password="password123"
    )
    user.profile.role = role
    user.profile.save()
    return user


class DashboardTests(TestCase):
    def setUp(self):
        self.admin = make_user("admin", ROLE_ADMIN)
        self.staff = make_user("staff", ROLE_STAFF)
        self.rep1 = make_user("rep1", ROLE_REP)
        self.rep2 = make_user("rep2", ROLE_REP)
        self.region = Region.objects.create(name="North")
        self.hospital = Hospital.objects.create(name="City", region=self.region)
        self.doctor = Doctor.objects.create(name="Chen", hospital=self.hospital)
        self.pharmacy = Pharmacy.objects.create(name="Olive", region=self.region)
        self.product = Product.objects.create(name="Cardiolex", sku="CARD-10")

        for rep, amount in ((self.rep1, "100.00"), (self.rep2, "300.00")):
            SalesLog.objects.create(
                rep=rep,
                entered_by=self.staff,
                sales_date="2026-01-10",
                region=self.region,
                hospital=self.hospital,
                doctor=self.doctor,
                pharmacy=self.pharmacy,
                product=self.product,
                quantity=1,
                amount=Decimal(amount),
            )

    def _dashboard(self):
        return self.client.get(
            reverse("dashboard:home"),
            {"start_date": "2026-01-01", "end_date": "2026-01-31"},
        )

    def test_rep_dashboard_is_scoped(self):
        self.client.force_login(self.rep1)
        response = self._dashboard()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["kpis"]["sales_amount"], Decimal("100.00"))

    def test_admin_dashboard_aggregates_all(self):
        self.client.force_login(self.admin)
        response = self._dashboard()
        self.assertEqual(response.context["kpis"]["sales_amount"], Decimal("400.00"))

    def test_reports_render(self):
        self.client.force_login(self.admin)
        for tab in ("monthly", "representatives", "hospitals", "products"):
            response = self.client.get(
                reverse("dashboard:reports"), {"tab": tab, "start_date": "2026-01-01", "end_date": "2026-01-31"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["active_tab"], tab)

    def test_csv_export_filters(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("dashboard:export"),
            {
                "report": "representatives",
                "start_date": "2026-01-01",
                "end_date": "2026-01-31",
                "rep": self.rep1.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode()
        self.assertIn("rep1", content)
        self.assertNotIn("rep2", content)
