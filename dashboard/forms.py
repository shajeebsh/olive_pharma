from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.managers import get_user_role
from core.models import Hospital, Product

INPUT = {"class": "form-control"}
SELECT = {"class": "form-select"}


class DashboardFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={**INPUT, "type": "date"})
    )
    end_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={**INPUT, "type": "date"})
    )
    rep = forms.ModelChoiceField(
        required=False, queryset=get_user_model().objects.none(), widget=forms.Select(attrs=SELECT)
    )
    hospital = forms.ModelChoiceField(
        required=False, queryset=Hospital.objects.none(), widget=forms.Select(attrs=SELECT)
    )
    product = forms.ModelChoiceField(
        required=False, queryset=Product.objects.none(), widget=forms.Select(attrs=SELECT)
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        role = get_user_role(user)
        self.show_rep = role in ("admin", "staff")
        if self.show_rep:
            self.fields["rep"].queryset = get_user_model().objects.filter(
                is_active=True
            )
        self.fields["hospital"].queryset = Hospital.objects.all()
        self.fields["product"].queryset = Product.objects.all()

    def clean(self):
        cleaned = super().clean()
        today = timezone.localdate()
        if not cleaned.get("start_date"):
            cleaned["start_date"] = today.replace(day=1)
        if not cleaned.get("end_date"):
            cleaned["end_date"] = today
        if cleaned.get("start_date") and cleaned.get("end_date"):
            if cleaned["start_date"] > cleaned["end_date"]:
                raise forms.ValidationError("Start date must be on or before end date.")
        if not self.show_rep:
            cleaned["rep"] = self.user
        return cleaned

    def as_filters(self):
        if not self.is_valid():
            return {
                "start_date": timezone.localdate().replace(day=1),
                "end_date": timezone.localdate(),
                "rep": None if self.show_rep else self.user,
                "hospital": None,
                "product": None,
            }
        return self.cleaned_data
