from django import forms

from .models import UserProfile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("phone", "employee_code", "region")
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "employee_code": forms.TextInput(attrs={"class": "form-control"}),
            "region": forms.Select(attrs={"class": "form-select"}),
        }
