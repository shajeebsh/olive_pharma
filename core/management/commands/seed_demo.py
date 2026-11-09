from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from checkin.models import CheckInOut
from core.models import Doctor, Hospital, Pharmacy, Product, Region
from sales.models import SalesLog, Target
from visits.models import ChemistVisit, DoctorVisit


class Command(BaseCommand):
    help = "Seed demo users and field-activity data for local development."

    def handle(self, *args, **options):
        User = get_user_model()
        users = {}
        for username, role, first, last in [
            ("admin", ROLE_ADMIN, "Ava", "Admin"),
            ("rep", ROLE_REP, "Ravi", "Rep"),
            ("staff", ROLE_STAFF, "Sara", "Staff"),
        ]:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "email": f"{username}@example.com"},
            )
            if created:
                user.set_password("password123")
                user.save()
            profile = user.profile
            profile.role = role
            profile.phone = "555-0100"
            profile.employee_code = f"EMP-{username.upper()}"
            profile.save()
            users[username] = user

        region, _ = Region.objects.get_or_create(
            name="Ernakulam",
            defaults={"code": "EKM", "state": "Kerala", "country": "India"},
        )
        hospital, _ = Hospital.objects.get_or_create(
            name="City General Hospital",
            defaults={"region": region, "city": "Kochi"},
        )
        doctor, _ = Doctor.objects.get_or_create(
            name="Maya Chen",
            defaults={"hospital": hospital, "speciality": "Cardiology"},
        )
        pharmacy, _ = Pharmacy.objects.get_or_create(
            name="Olive Pharmacy",
            defaults={"region": region, "hospital": hospital, "locality": "Downtown"},
        )
        products = []
        for name, sku, form, strength in [
            ("Cardiolex", "CARD-10", "Tablet", "10mg"),
            ("Glucobal", "GLU-500", "Tablet", "500mg"),
            ("Neutriva", "NEU-25", "Capsule", "25mg"),
        ]:
            product, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={"name": name, "form": form, "strength": strength},
            )
            products.append(product)

        today = timezone.localdate()
        rep = users["rep"]

        doctor_visit, _ = DoctorVisit.objects.get_or_create(
            rep=rep,
            date=today,
            doctor=doctor,
            defaults={
                "region": region,
                "hospital": hospital,
                "notes": "Introductory detail.",
            },
        )
        doctor_visit.products_introduced.set(products[:2])

        chemist_visit, _ = ChemistVisit.objects.get_or_create(
            rep=rep,
            date=today,
            pharmacy=pharmacy,
            defaults={
                "region": region,
                "hospital": hospital,
                "doctor": doctor,
                "current_products": "Cardiolex",
                "quantity": 20,
                "notes": "Requested Glucobal samples.",
            },
        )
        chemist_visit.products_needed.set(products[1:])

        SalesLog.objects.get_or_create(
            rep=rep,
            reference="INV-DEMO-001",
            defaults={
                "entered_by": users["staff"],
                "sales_date": today,
                "region": region,
                "hospital": hospital,
                "doctor": doctor,
                "pharmacy": pharmacy,
                "product": products[0],
                "quantity": 12,
                "amount": Decimal("480.00"),
            },
        )

        month_start = today.replace(day=1)
        Target.objects.get_or_create(
            rep=rep,
            product=products[0],
            start_date=month_start,
            end_date=today + timedelta(days=20),
            defaults={
                "period": Target.PERIOD_MONTH,
                "amount_target": Decimal("1000.00"),
                "quantity_target": 30,
            },
        )

        CheckInOut.objects.get_or_create(
            user=rep,
            date=today,
            defaults={"check_in": time(9, 0)},
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded. Login: admin/rep/staff, password123."))
