from django.contrib import admin

from .models import ChemistVisit, DoctorVisit


@admin.register(DoctorVisit)
class DoctorVisitAdmin(admin.ModelAdmin):
    list_display = ("rep", "date", "doctor", "hospital", "region")
    list_filter = ("date", "region", "hospital")
    search_fields = ("rep__username", "doctor__name", "hospital__name")
    filter_horizontal = ("products_introduced",)


@admin.register(ChemistVisit)
class ChemistVisitAdmin(admin.ModelAdmin):
    list_display = ("rep", "date", "pharmacy", "doctor", "hospital", "region")
    list_filter = ("date", "region", "hospital")
    search_fields = ("rep__username", "pharmacy__name", "doctor__name")
    filter_horizontal = ("products_needed",)
