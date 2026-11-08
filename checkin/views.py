from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import FormView, ListView

from core.permissions import RoleRequiredMixin

from .forms import CheckInForm, CheckOutForm
from .models import CheckInOut
from .services import check_in, check_out


class CheckInListView(RoleRequiredMixin, ListView):
    allowed_roles = ("admin", "staff", "rep")
    model = CheckInOut
    template_name = "checkin/list.html"
    context_object_name = "checkins"
    paginate_by = 30

    def get_queryset(self):
        return CheckInOut.objects.for_user(
            self.request.user, "user", staff_company_wide=False
        )


class CheckInView(RoleRequiredMixin, FormView):
    allowed_roles = ("admin", "staff", "rep")
    form_class = CheckInForm
    template_name = "checkin/check_in.html"

    def form_valid(self, form):
        try:
            check_in(
                user=self.request.user,
                date=form.cleaned_data["date"],
                check_in_time=form.cleaned_data["check_in"],
                notes=form.cleaned_data["notes"],
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Checked in.")
        return redirect("checkin:list")


class CheckOutView(RoleRequiredMixin, FormView):
    allowed_roles = ("admin", "staff", "rep")
    form_class = CheckOutForm
    template_name = "checkin/check_out.html"

    def form_valid(self, form):
        try:
            check_out(
                user=self.request.user,
                date=form.cleaned_data["date"],
                check_out_time=form.cleaned_data["check_out"],
                notes=form.cleaned_data["notes"],
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        messages.success(self.request, "Checked out.")
        return redirect("checkin:list")
