from django import forms

from .models import Product

INPUT = {"class": "form-control"}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "sku", "form", "strength", "active")
        widgets = {
            "name": forms.TextInput(attrs=INPUT),
            "sku": forms.TextInput(attrs=INPUT),
            "form": forms.TextInput(attrs=INPUT),
            "strength": forms.TextInput(attrs=INPUT),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
