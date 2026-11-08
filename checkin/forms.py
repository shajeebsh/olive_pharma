from django import forms
from django.utils import timezone

INPUT = {"class": "form-control"}


class CheckInForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={**INPUT, "type": "date"}),
        initial=timezone.localdate,
    )
    check_in = forms.TimeField(
        widget=forms.TimeInput(attrs={**INPUT, "type": "time"}),
        initial=lambda: timezone.localtime().time().replace(microsecond=0),
    )
    notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={**INPUT, "rows": 3})
    )


class CheckOutForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={**INPUT, "type": "date"}),
        initial=timezone.localdate,
    )
    check_out = forms.TimeField(
        widget=forms.TimeInput(attrs={**INPUT, "type": "time"}),
        initial=lambda: timezone.localtime().time().replace(microsecond=0),
    )
    notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={**INPUT, "rows": 3})
    )
