from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView

from core.permissions import RoleRequiredMixin

from .forms import SalesLogForm, TargetForm
from .models import SalesLog, Target
from .services import log_sales


class SalesLogListView(RoleRequiredMixin, ListView):
    allowed_roles = ("admin", "staff", "rep")
    model = SalesLog
    template_name = "sales/list.html"
    context_object_name = "sales"
    paginate_by = 20

    def get_queryset(self):
        return (
            SalesLog.objects.for_user(self.request.user, "rep")
            .select_related("rep", "region", "hospital", "doctor", "pharmacy", "product")
        )


class SalesLogCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ("admin", "staff")
    model = SalesLog
    form_class = SalesLogForm
    template_name = "sales/form.html"

    def form_valid(self, form):
        log_sales(data=form.cleaned_data, entered_by=self.request.user)
        messages.success(self.request, "Sales entry logged.")
        return redirect("sales:list")


class TargetListView(RoleRequiredMixin, ListView):
    allowed_roles = ("admin", "staff", "rep")
    model = Target
    template_name = "sales/target_list.html"
    context_object_name = "targets"
    paginate_by = 20

    def get_queryset(self):
        return Target.objects.for_user(self.request.user, "rep").select_related(
            "rep", "product"
        )


class TargetCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ("admin",)
    model = Target
    form_class = TargetForm
    template_name = "sales/target_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Target saved.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("sales:target_list")
