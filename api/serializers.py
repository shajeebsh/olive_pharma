"""Serializers for the mobile (Flutter) REST API.

Read endpoints expose human-readable labels alongside primary keys so the app
can render lists without extra lookups. Write endpoints accept primary keys and
delegate to the existing service layer where side effects (signals, audit) live.
"""

from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import UserProfile
from checkin.models import CheckInOut
from core.managers import get_user_role
from core.models import Doctor, Hospital, Pharmacy, Product, Region
from sales.models import SalesLog
from visits.models import ChemistVisit, DoctorVisit
from visits.services import log_chemist_visit, log_doctor_visit


class LoginSerializer(TokenObtainPairSerializer):
    """JWT login that also returns the caller's profile summary."""

    def validate(self, attrs):
        data = super().validate(attrs)
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        data["user"] = UserProfileSerializer(profile).data
        return data


class RegionSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = Region
        fields = ("id", "name", "code", "state", "country", "label")


class HospitalSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)

    class Meta:
        model = Hospital
        fields = ("id", "name", "region", "region_name", "city", "address")


class DoctorSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(source="hospital.name", read_only=True)

    class Meta:
        model = Doctor
        fields = ("id", "name", "hospital", "hospital_name", "speciality", "phone")


class PharmacySerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)
    hospital_name = serializers.CharField(
        source="hospital.name", read_only=True, default=None
    )

    class Meta:
        model = Pharmacy
        fields = (
            "id",
            "name",
            "region",
            "region_name",
            "hospital",
            "hospital_name",
            "locality",
            "phone",
        )


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "sku", "form", "strength", "active")


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    region_name = serializers.CharField(source="region.name", read_only=True, default=None)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "employee_code",
            "region",
            "region_name",
        )
        read_only_fields = ("id", "username", "email", "role")


class _FutureDateMixin:
    """Reject future dates for representatives; admins may pre-enter records."""

    def validate_date(self, value):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if value > timezone.localdate() and get_user_role(user) != "admin":
            raise serializers.ValidationError("Date cannot be in the future.")
        return value


class DoctorVisitSerializer(_FutureDateMixin, serializers.ModelSerializer):
    rep_name = serializers.CharField(source="rep.username", read_only=True)
    region_name = serializers.CharField(source="region.name", read_only=True)
    hospital_name = serializers.CharField(source="hospital.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    products_introduced = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.filter(active=True),
        required=False,
    )
    products_introduced_detail = ProductSerializer(
        source="products_introduced", many=True, read_only=True
    )

    class Meta:
        model = DoctorVisit
        fields = (
            "id",
            "date",
            "region",
            "region_name",
            "hospital",
            "hospital_name",
            "doctor",
            "doctor_name",
            "products_introduced",
            "products_introduced_detail",
            "notes",
            "rep_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "rep_name")

    def create(self, validated_data):
        rep = self.context["request"].user
        return log_doctor_visit(rep=rep, data=validated_data)


class ChemistVisitSerializer(_FutureDateMixin, serializers.ModelSerializer):
    rep_name = serializers.CharField(source="rep.username", read_only=True)
    region_name = serializers.CharField(source="region.name", read_only=True)
    hospital_name = serializers.CharField(source="hospital.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    pharmacy_name = serializers.CharField(source="pharmacy.name", read_only=True)
    products_needed = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.filter(active=True),
        required=False,
    )
    products_needed_detail = ProductSerializer(
        source="products_needed", many=True, read_only=True
    )

    class Meta:
        model = ChemistVisit
        fields = (
            "id",
            "date",
            "region",
            "region_name",
            "hospital",
            "hospital_name",
            "doctor",
            "doctor_name",
            "pharmacy",
            "pharmacy_name",
            "current_products",
            "products_needed",
            "products_needed_detail",
            "quantity",
            "notes",
            "rep_name",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "rep_name")

    def create(self, validated_data):
        rep = self.context["request"].user
        return log_chemist_visit(rep=rep, data=validated_data)


class SalesLogSerializer(serializers.ModelSerializer):
    rep_name = serializers.CharField(source="rep.username", read_only=True)
    region_name = serializers.CharField(source="region.name", read_only=True)
    hospital_name = serializers.CharField(source="hospital.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    pharmacy_name = serializers.CharField(source="pharmacy.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = SalesLog
        fields = (
            "id",
            "sales_date",
            "rep_name",
            "region_name",
            "hospital_name",
            "doctor_name",
            "pharmacy_name",
            "product_name",
            "quantity",
            "amount",
            "reference",
            "notes",
        )
        read_only_fields = fields


class CheckInSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    duration = serializers.SerializerMethodField()
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = CheckInOut
        fields = (
            "id",
            "date",
            "check_in",
            "check_out",
            "notes",
            "duration",
            "is_open",
            "user_name",
        )
        read_only_fields = ("id", "user_name", "duration", "is_open")

    def get_duration(self, obj):
        return str(obj.duration) if obj.duration else None


class CheckInRequestSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)
    check_in = serializers.TimeField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class CheckOutRequestSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)
    check_out = serializers.TimeField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
