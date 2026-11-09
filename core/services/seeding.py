import uuid
from datetime import time, timedelta
from decimal import Decimal

from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from accounts.models import ROLE_REP
from checkin.models import CheckInOut
from core.models import AuditLog, Doctor, Hospital, Pharmacy, Product, Region
from sales.models import SalesLog, Target
from visits.models import ChemistVisit, DoctorVisit

PRODUCT_FORMS = ("Tablet", "Capsule", "Syrup", "Injection")
KERALA_STATE = "Kerala"
COUNTRY = "India"
KERALA_DISTRICTS = (
    "Thiruvananthapuram",
    "Kollam",
    "Pathanamthitta",
    "Alappuzha",
    "Kottayam",
    "Idukki",
    "Ernakulam",
    "Thrissur",
    "Palakkad",
    "Malappuram",
    "Kozhikode",
    "Wayanad",
    "Kannur",
    "Kasaragod",
)


def _unique(prefix=""):
    value = uuid.uuid4().hex[:10].upper()
    return f"{prefix}{value}" if prefix else value


def _create_region(fake):
    existing = set(Region.objects.values_list("name", flat=True))
    available = [name for name in KERALA_DISTRICTS if name not in existing]
    if not available:
        return None
    name = fake.random_element(available)
    return Region.objects.create(
        name=name,
        code=name[:3].upper(),
        state=KERALA_STATE,
        country=COUNTRY,
    )


def _get_user(fake):
    user = get_user_model().objects.order_by("?").first()
    if user is not None:
        return user
    user = get_user_model().objects.create_user(
        username=f"seed_{_unique().lower()}", password="password123"
    )
    user.profile.role = ROLE_REP
    user.profile.save()
    return user


def _get_region(fake):
    region = Region.objects.order_by("?").first()
    if region is not None:
        return region
    return _create_region(fake)


def _get_hospital(fake, region=None):
    hospitals = Hospital.objects.all()
    if region is not None:
        hospitals = hospitals.filter(region=region)
    hospital = hospitals.order_by("?").first()
    if hospital is not None:
        return hospital
    return Hospital.objects.create(
        name=f"{fake.company()} Hospital",
        region=region or _get_region(fake),
        city=fake.city(),
        address=fake.address(),
    )


def _get_doctor(fake, hospital=None):
    doctors = Doctor.objects.all()
    if hospital is not None:
        doctors = doctors.filter(hospital=hospital)
    doctor = doctors.order_by("?").first()
    if doctor is not None:
        return doctor
    return Doctor.objects.create(
        name=f"{fake.first_name()} {fake.last_name()}",
        hospital=hospital or _get_hospital(fake),
        speciality=fake.word().title(),
        phone=fake.phone_number()[:40],
    )


def _get_pharmacy(fake, region=None, hospital=None):
    pharmacies = Pharmacy.objects.all()
    if region is not None:
        pharmacies = pharmacies.filter(region=region)
    if hospital is not None:
        pharmacies = pharmacies.filter(hospital=hospital)
    pharmacy = pharmacies.order_by("?").first()
    if pharmacy is not None:
        return pharmacy
    region = region or _get_region(fake)
    return Pharmacy.objects.create(
        name=f"{fake.company()} Pharmacy",
        region=region,
        hospital=hospital or _get_hospital(fake, region),
        locality=fake.city(),
        phone=fake.phone_number()[:40],
    )


def _get_product(fake):
    product = Product.objects.order_by("?").first()
    if product is not None:
        return product
    return Product.objects.create(
        name=fake.word().title(),
        sku=_unique("SKU-"),
        form=fake.random_element(PRODUCT_FORMS),
        strength=f"{fake.random_int(1, 500)}mg",
    )


def seed_region(fake):
    return _create_region(fake) is not None


def seed_hospital(fake):
    region = _get_region(fake)
    Hospital.objects.create(
        name=f"{fake.company()} Hospital",
        region=region,
        city=fake.city(),
        address=fake.address(),
    )
    return True


def seed_doctor(fake):
    hospital = _get_hospital(fake)
    Doctor.objects.create(
        name=f"{fake.first_name()} {fake.last_name()}",
        hospital=hospital,
        speciality=fake.word().title(),
        phone=fake.phone_number()[:40],
    )
    return True


def seed_pharmacy(fake):
    region = _get_region(fake)
    hospital = _get_hospital(fake, region)
    Pharmacy.objects.create(
        name=f"{fake.company()} Pharmacy",
        region=region,
        hospital=hospital,
        locality=fake.city(),
        phone=fake.phone_number()[:40],
    )
    return True


def seed_product(fake):
    Product.objects.create(
        name=fake.word().title(),
        sku=_unique("SKU-"),
        form=fake.random_element(PRODUCT_FORMS),
        strength=f"{fake.random_int(1, 500)}mg",
    )
    return True


def seed_audit_log(fake):
    AuditLog.objects.create(
        user=_get_user(fake),
        action="seed_sample",
        object_type="Seed",
        object_id=_unique(),
        changes={"source": "seed_table"},
    )
    return True


def seed_doctor_visit(fake):
    region = _get_region(fake)
    hospital = _get_hospital(fake, region)
    doctor = _get_doctor(fake, hospital)
    visit = DoctorVisit.objects.create(
        rep=_get_user(fake),
        date=fake.date_between(start_date="-30d", end_date="today"),
        region=region,
        hospital=hospital,
        doctor=doctor,
        notes=fake.sentence(),
    )
    products = list(Product.objects.order_by("?")[: fake.random_int(1, 3)])
    if not products:
        products = [_get_product(fake)]
    visit.products_introduced.set(products)
    return True


def seed_chemist_visit(fake):
    region = _get_region(fake)
    hospital = _get_hospital(fake, region)
    visit = ChemistVisit.objects.create(
        rep=_get_user(fake),
        date=fake.date_between(start_date="-30d", end_date="today"),
        region=region,
        hospital=hospital,
        doctor=_get_doctor(fake, hospital),
        pharmacy=_get_pharmacy(fake, region, hospital),
        current_products=fake.sentence(),
        quantity=fake.random_int(1, 100),
        notes=fake.sentence(),
    )
    products = list(Product.objects.order_by("?")[: fake.random_int(1, 3)])
    if not products:
        products = [_get_product(fake)]
    visit.products_needed.set(products)
    return True


def seed_sales_log(fake):
    region = _get_region(fake)
    hospital = _get_hospital(fake, region)
    SalesLog.objects.create(
        rep=_get_user(fake),
        entered_by=_get_user(fake),
        sales_date=fake.date_between(start_date="-30d", end_date="today"),
        region=region,
        hospital=hospital,
        doctor=_get_doctor(fake, hospital),
        pharmacy=_get_pharmacy(fake, region, hospital),
        product=_get_product(fake),
        quantity=fake.random_int(1, 50),
        amount=Decimal(fake.random_int(50, 5000)),
        reference=_unique("SEED-"),
        notes=fake.sentence(),
    )
    return True


def seed_target(fake):
    start_date = timezone.localdate() - timedelta(days=fake.random_int(0, 180))
    _, created = Target.objects.get_or_create(
        rep=_get_user(fake),
        product=_get_product(fake),
        start_date=start_date,
        end_date=start_date + timedelta(days=30),
        defaults={
            "period": fake.random_element(
                (Target.PERIOD_MONTH, Target.PERIOD_QUARTER)
            ),
            "amount_target": Decimal(fake.random_int(1000, 20000)),
            "quantity_target": fake.random_int(10, 500),
        },
    )
    return created


def seed_checkin(fake):
    check_in = fake.time_object()
    check_out = time(
        min(check_in.hour + fake.random_int(1, 6), 23),
        fake.random_int(0, 59),
    )
    _, created = CheckInOut.objects.get_or_create(
        user=_get_user(fake),
        date=fake.date_between(start_date="-60d", end_date="today"),
        defaults={
            "check_in": check_in,
            "check_out": check_out,
            "notes": fake.sentence(),
        },
    )
    return created


SEEDERS = {
    "core.Region": seed_region,
    "core.Hospital": seed_hospital,
    "core.Doctor": seed_doctor,
    "core.Pharmacy": seed_pharmacy,
    "core.Product": seed_product,
    "core.AuditLog": seed_audit_log,
    "visits.DoctorVisit": seed_doctor_visit,
    "visits.ChemistVisit": seed_chemist_visit,
    "sales.SalesLog": seed_sales_log,
    "sales.Target": seed_target,
    "checkin.CheckInOut": seed_checkin,
}


def seedable_models():
    choices = []
    for label in SEEDERS:
        app_label, model_name = label.split(".")
        model = apps.get_model(app_label, model_name)
        choices.append(
            {
                "label": label,
                "name": f"{model._meta.verbose_name} ({label})",
            }
        )
    return sorted(choices, key=lambda item: item["name"].lower())


def seed_rows(label, rows):
    seeder = SEEDERS.get(label)
    if seeder is None:
        raise ValueError(f"Unsupported model for seeding: {label}")
    fake = Faker()
    created = 0
    for _ in range(rows):
        if seeder(fake):
            created += 1
    return created
