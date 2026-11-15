"""JSON API consumed by the OlivePharma Flutter representative app.

All endpoints require JWT authentication. Read endpoints reuse the existing
``ScopedManager.for_user`` so representatives only ever see their own records.
Write endpoints delegate to the ``visits`` and ``checkin`` service layer so the
audit signals and business rules stay in one place.
"""

from datetime import date

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from checkin.models import CheckInOut
from checkin.services import check_in as check_in_service
from checkin.services import check_out as check_out_service
from core.models import Doctor, Hospital, Pharmacy, Product, Region
from dashboard.services import kpis as kpis_service
from dashboard.services import recent_activity
from sales.models import SalesLog
from visits.models import ChemistVisit, DoctorVisit

from .pagination import StandardPagination
from .permissions import IsRepresentativeOrAdmin
from .serializers import (
    CheckInRequestSerializer,
    CheckInSerializer,
    CheckOutRequestSerializer,
    ChemistVisitSerializer,
    DoctorSerializer,
    DoctorVisitSerializer,
    HospitalSerializer,
    LoginSerializer,
    PharmacySerializer,
    ProductSerializer,
    RegionSerializer,
    SalesLogSerializer,
    UserProfileSerializer,
)


# ── Auth ──────────────────────────────────────────────────────────────────────
class LoginView(TokenObtainPairView):
    """Issue a JWT access/refresh pair plus the caller's profile summary."""

    serializer_class = LoginSerializer


# ── Masters ───────────────────────────────────────────────────────────────────
class RegionListView(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ("name", "state", "country")


class HospitalListView(generics.ListAPIView):
    queryset = Hospital.objects.select_related("region").all()
    serializer_class = HospitalSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("region",)
    search_fields = ("name",)


class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.select_related("hospital").all()
    serializer_class = DoctorSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("hospital",)
    search_fields = ("name", "speciality")


class PharmacyListView(generics.ListAPIView):
    queryset = Pharmacy.objects.select_related("region", "hospital").all()
    serializer_class = PharmacySerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("region", "hospital")
    search_fields = ("name", "locality")


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("active",)
    search_fields = ("name", "sku")

    def get_queryset(self):
        return Product.objects.all()


# ── Profile ───────────────────────────────────────────────────────────────────
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        from accounts.models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


# ── Field activity ────────────────────────────────────────────────────────────
class DoctorVisitListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorVisitSerializer
    permission_classes = (IsAuthenticated, IsRepresentativeOrAdmin)
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            DoctorVisit.objects.for_user(self.request.user, "rep")
            .select_related("region", "hospital", "doctor", "rep")
            .prefetch_related("products_introduced")
        )


class ChemistVisitListCreateView(generics.ListCreateAPIView):
    serializer_class = ChemistVisitSerializer
    permission_classes = (IsAuthenticated, IsRepresentativeOrAdmin)
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            ChemistVisit.objects.for_user(self.request.user, "rep")
            .select_related("region", "hospital", "doctor", "pharmacy", "rep")
            .prefetch_related("products_needed")
        )


# ── Sales (read-only, own records) ────────────────────────────────────────────
class SalesLogListView(generics.ListAPIView):
    serializer_class = SalesLogSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            SalesLog.objects.for_user(self.request.user, "rep")
            .select_related(
                "rep", "region", "hospital", "doctor", "pharmacy", "product"
            )
        )


# ── Attendance ────────────────────────────────────────────────────────────────
class CheckInListView(generics.ListAPIView):
    serializer_class = CheckInSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):
        return CheckInOut.objects.for_user(
            self.request.user, "user", staff_company_wide=False
        )


class CheckInCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CheckInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            record = check_in_service(
                user=request.user,
                date=data.get("date"),
                check_in_time=data.get("check_in"),
                notes=data.get("notes", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError({"detail": exc.messages})
        return Response(CheckInSerializer(record).data, status=status.HTTP_201_CREATED)


class CheckOutCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CheckOutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            record = check_out_service(
                user=request.user,
                date=data.get("date"),
                check_out_time=data.get("check_out"),
                notes=data.get("notes", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError({"detail": exc.messages})
        return Response(CheckInSerializer(record).data, status=status.HTTP_200_OK)


# ── Dependent filter options (region → hospital → doctor/pharmacy) ────────────
class FilterOptionsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        kind = request.query_params.get("type")
        if kind == "hospital":
            region_id = _as_int(request.query_params.get("region"))
            if region_id is None:
                return Response({"results": []})
            rows = Hospital.objects.filter(region_id=region_id).order_by("name")
            results = [{"id": row.id, "text": row.name} for row in rows]
        elif kind == "doctor":
            hospital_id = _as_int(request.query_params.get("hospital"))
            if hospital_id is None:
                return Response({"results": []})
            rows = Doctor.objects.filter(hospital_id=hospital_id).order_by("name")
            results = [{"id": row.id, "text": f"Dr. {row.name}"} for row in rows]
        elif kind == "pharmacy":
            hospital_id = _as_int(request.query_params.get("hospital"))
            if hospital_id is None:
                return Response({"results": []})
            rows = Pharmacy.objects.filter(hospital_id=hospital_id).order_by("name")
            results = [{"id": row.id, "text": row.name} for row in rows]
        else:
            raise ValidationError({"detail": "Unknown option type."})
        return Response({"results": results})


# ── Dashboard (own data) ──────────────────────────────────────────────────────
class DashboardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        start, end = _date_range(request)
        filters = {"start_date": start, "end_date": end}
        data = kpis_service(request.user, filters)
        recent = []
        for item in recent_activity(request.user, filters, limit=5):
            obj = item["obj"]
            if item["kind"] == "doctor":
                recent.append(
                    {
                        "kind": "doctor",
                        "id": obj.id,
                        "date": obj.date,
                        "title": f"Dr. {obj.doctor.name}",
                        "subtitle": obj.hospital.name,
                    }
                )
            else:
                recent.append(
                    {
                        "kind": "chemist",
                        "id": obj.id,
                        "date": obj.date,
                        "title": obj.pharmacy.name,
                        "subtitle": obj.hospital.name,
                    }
                )
        return Response(
            {
                "start_date": start,
                "end_date": end,
                "kpis": data,
                "recent_visits": recent,
            }
        )


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _date_range(request):
    today = timezone.localdate()
    start = _parse_date(request.query_params.get("start")) or today.replace(day=1)
    end = _parse_date(request.query_params.get("end")) or today
    return start, end


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None
