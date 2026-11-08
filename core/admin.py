from django.contrib import admin

from .models import AuditLog, Doctor, Hospital, Pharmacy, Product, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "city")
    list_filter = ("region",)
    search_fields = ("name", "city")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "hospital", "speciality")
    list_filter = ("hospital",)
    search_fields = ("name", "speciality")


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "hospital", "locality")
    list_filter = ("region",)
    search_fields = ("name", "locality")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "form", "strength", "active")
    list_filter = ("active", "form")
    search_fields = ("name", "sku")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "object_type", "object_id", "user", "created_at")
    list_filter = ("action", "object_type")
    search_fields = ("object_type", "object_id")
    readonly_fields = (
        "user",
        "action",
        "object_type",
        "object_id",
        "changes",
        "created_at",
    )
