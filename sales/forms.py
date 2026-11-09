from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.managers import get_user_role
from core.models import Doctor, Hospital, Pharmacy, Product, Region

from .models import SalesLog, Target

INPUT = {"class": "form-control"}
SELECT = {"class": "form-select"}


class SalesLogForm(forms.ModelForm):
    class Meta:
        model = SalesLog
        fields = (
            "rep",
            "sales_date",
            "region",
            "hospital",
            "doctor",
            "pharmacy",
            "product",
            "quantity",
            "amount",
            "reference",
            "notes",
        )
        widgets = {
            "rep": forms.Select(attrs=SELECT),
            "sales_date": forms.DateInput(attrs={**INPUT, "type": "date"}),
            "region": forms.Select(attrs=SELECT),
            "hospital": forms.Select(attrs=SELECT),
            "doctor": forms.Select(attrs=SELECT),
            "pharmacy": forms.Select(attrs=SELECT),
            "product": forms.Select(attrs=SELECT),
            "quantity": forms.NumberInput(attrs={**INPUT, "min": 1}),
            "amount": forms.NumberInput(attrs={**INPUT, "step": "0.01", "min": 0}),
            "reference": forms.TextInput(attrs=INPUT),
            "notes": forms.Textarea(attrs={**INPUT, "rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["rep"].queryset = get_user_model().objects.filter(is_active=True)
        self.fields["region"].queryset = Region.objects.all()
        self.fields["hospital"].queryset = Hospital.objects.all()
        self.fields["doctor"].queryset = Doctor.objects.select_related("hospital")
        self.fields["pharmacy"].queryset = Pharmacy.objects.all()
        self.fields["product"].queryset = Product.objects.filter(active=True)

    def clean_sales_date(self):
        value = self.cleaned_data.get("sales_date")
        if not value:
            return value
        if value > timezone.localdate() and get_user_role(self.user) != "admin":
            raise forms.ValidationError("Date cannot be in the future.")
        return value

    def clean(self):
        cleaned = super().clean()
        rep = cleaned.get("rep")
        reference = cleaned.get("reference")
        if rep and reference:
            duplicates = SalesLog.objects.filter(rep=rep, reference=reference)
            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                self.add_error(
                    "reference",
                    "This reference already exists for the selected representative.",
                )
        return cleaned


class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = (
            "rep",
            "period",
            "start_date",
            "end_date",
            "product",
            "amount_target",
            "quantity_target",
        )
        widgets = {
            "rep": forms.Select(attrs=SELECT),
            "period": forms.Select(attrs=SELECT),
            "start_date": forms.DateInput(attrs={**INPUT, "type": "date"}),
            "end_date": forms.DateInput(attrs={**INPUT, "type": "date"}),
            "product": forms.Select(attrs=SELECT),
            "amount_target": forms.NumberInput(
                attrs={**INPUT, "step": "0.01", "min": 0}
            ),
            "quantity_target": forms.NumberInput(attrs={**INPUT, "min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rep"].queryset = get_user_model().objects.filter(is_active=True)
        self.fields["product"].queryset = Product.objects.filter(active=True)
