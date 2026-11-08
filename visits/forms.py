from django import forms

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.all()
        self.fields["hospital"].queryset = Hospital.objects.all()
        self.fields["doctor"].queryset = Doctor.objects.select_related("hospital")
        self.fields["products_introduced"].queryset = Product.objects.filter(active=True)


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
            "notes": forms.Textarea(attrs={**INPUT, "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.all()
        self.fields["hospital"].queryset = Hospital.objects.all()
        self.fields["doctor"].queryset = Doctor.objects.select_related("hospital")
        self.fields["pharmacy"].queryset = Pharmacy.objects.all()
        self.fields["products_needed"].queryset = Product.objects.filter(active=True)
