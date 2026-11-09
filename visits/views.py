from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView

from core.models import Doctor, Hospital, Pharmacy
from core.permissions import RoleRequiredMixin, role_required

from .forms import ChemistVisitForm, DoctorVisitForm
from .models import ChemistVisit, DoctorVisit
from .services import log_chemist_visit, log_doctor_visit


@role_required("admin", "rep")
def filter_options(request):
    kind = request.GET.get("type")

    if kind == "hospital":
        region_id = _as_int(request.GET.get("region"))
        if region_id is None:
            return JsonResponse({"results": []})
        rows = (
            Hospital.objects.filter(region_id=region_id)
            .order_by("name")
            .values("id", "name")
        )
        results = [{"id": row["id"], "text": row["name"]} for row in rows]
    elif kind == "doctor":
        hospital_id = _as_int(request.GET.get("hospital"))
        if hospital_id is None:
            return JsonResponse({"results": []})
        rows = (
            Doctor.objects.filter(hospital_id=hospital_id)
            .order_by("name")
            .values("id", "name")
        )
        results = [{"id": row["id"], "text": f"Dr. {row['name']}"} for row in rows]
    elif kind == "pharmacy":
        hospital_id = _as_int(request.GET.get("hospital"))
        if hospital_id is None:
            return JsonResponse({"results": []})
        rows = (
            Pharmacy.objects.filter(hospital_id=hospital_id)
            .order_by("name")
            .values("id", "name")
        )
        results = [{"id": row["id"], "text": row["name"]} for row in rows]
    else:
        return JsonResponse({"error": "Unknown option type."}, status=400)

    return JsonResponse({"results": results})


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class DoctorVisitListView(RoleRequiredMixin, ListView):
    allowed_roles = ("admin", "rep")
    model = DoctorVisit
    template_name = "visits/doctor_list.html"
    context_object_name = "visits"
    paginate_by = 20

    def get_queryset(self):
        return (
            DoctorVisit.objects.for_user(self.request.user, "rep")
            .select_related("region", "hospital", "doctor")
            .prefetch_related("products_introduced")
        )


class DoctorVisitCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ("admin", "rep")
    model = DoctorVisit
    form_class = DoctorVisitForm
    template_name = "visits/doctor_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        log_doctor_visit(rep=self.request.user, data=form.cleaned_data)
        messages.success(self.request, "Doctor visit logged.")
        return redirect("visits:doctor_list")


class ChemistVisitListView(RoleRequiredMixin, ListView):
    allowed_roles = ("admin", "rep")
    model = ChemistVisit
    template_name = "visits/chemist_list.html"
    context_object_name = "visits"
    paginate_by = 20

    def get_queryset(self):
        return (
            ChemistVisit.objects.for_user(self.request.user, "rep")
            .select_related("region", "hospital", "doctor", "pharmacy")
            .prefetch_related("products_needed")
        )


class ChemistVisitCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ("admin", "rep")
    model = ChemistVisit
    form_class = ChemistVisitForm
    template_name = "visits/chemist_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        log_chemist_visit(rep=self.request.user, data=form.cleaned_data)
        messages.success(self.request, "Chemist visit logged.")
        return redirect("visits:chemist_list")
