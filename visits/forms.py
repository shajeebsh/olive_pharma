from django import forms
from django.utils import timezone

from core.managers import get_user_role
from core.models import Doctor, Hospital, Pharmacy, Product, Region

from .models import ChemistVisit, DoctorVisit

INPUT = {"class": "form-control"}
SELECT = {"class": "form-select"}


class DoctorVisitForm(forms.ModelForm):
    class Meta:
        model = DoctorVisit
        fields = (
            "date",
            "region",
            "hospital",
            "doctor",
            "products_introduced",
            "notes",
        )
        widgets = {
            "date": forms.DateInput(attrs={**INPUT, "type": "date"}),
            "region": forms.Select(attrs=SELECT),
            "hospital": forms.Select(attrs=SELECT),
            "doctor": forms.Select(attrs=SELECT),
            "products_introduced": forms.SelectMultiple(attrs=SELECT),
            "notes": forms.Textarea(attrs={**INPUT, "rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.all()
        self.fields["hospital"].queryset = Hospital.objects.all()
        self.fields["doctor"].queryset = Doctor.objects.select_related("hospital")
        self.fields["products_introduced"].queryset = Product.objects.filter(active=True)
        self.fields["products_introduced"].help_text = (
            "Select one or more products introduced during the visit."
        )

    def clean_date(self):
        value = self.cleaned_data.get("date")
        if not value:
            return value
        if value > timezone.localdate() and get_user_role(self.user) != "admin":
            raise forms.ValidationError("Date cannot be in the future.")
        return value


class ChemistVisitForm(forms.ModelForm):
    class Meta:
        model = ChemistVisit
        fields = (
            "date",
            "region",
            "hospital",
            "doctor",
            "pharmacy",
            "current_products",
            "products_needed",
            "quantity",
            "notes",
        )
        widgets = {
            "date": forms.DateInput(attrs={**INPUT, "type": "date"}),
            "region": forms.Select(attrs=SELECT),
            "hospital": forms.Select(attrs=SELECT),
            "doctor": forms.Select(attrs=SELECT),
            "pharmacy": forms.Select(attrs=SELECT),
            "current_products": forms.Textarea(attrs={**INPUT, "rows": 2}),
            "products_needed": forms.SelectMultiple(attrs=SELECT),
            "quantity": forms.NumberInput(attrs={**INPUT, "min": 1}),
            "notes": forms.Textarea(attrs={**INPUT, "rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.all()
        self.fields["hospital"].queryset = Hospital.objects.all()
        self.fields["doctor"].queryset = Doctor.objects.select_related("hospital")
        self.fields["pharmacy"].queryset = Pharmacy.objects.all()
        self.fields["products_needed"].queryset = Product.objects.filter(active=True)
        self.fields["products_needed"].help_text = (
            "Select the products requested by the pharmacy."
        )

    def clean_date(self):
        value = self.cleaned_data.get("date")
        if not value:
            return value
        if value > timezone.localdate() and get_user_role(self.user) != "admin":
            raise forms.ValidationError("Date cannot be in the future.")
        return value
