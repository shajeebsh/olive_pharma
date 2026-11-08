from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView

from core.permissions import RoleRequiredMixin

from .forms import ChemistVisitForm, DoctorVisitForm
from .models import ChemistVisit, DoctorVisit
from .services import log_chemist_visit, log_doctor_visit


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

    def form_valid(self, form):
        log_chemist_visit(rep=self.request.user, data=form.cleaned_data)
        messages.success(self.request, "Chemist visit logged.")
        return redirect("visits:chemist_list")
