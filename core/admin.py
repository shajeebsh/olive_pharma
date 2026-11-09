from django.contrib import admin
from django.urls import path

from .admin_views import db_profiling_view, seed_table_view
from .models import AuditLog, Doctor, Hospital, Pharmacy, Product, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("db-profiling/", db_profiling_view, name="db_profiling"),
            path("db-profiling/seed/", seed_table_view, name="db_profiling_seed"),
        ]
        return custom + urls


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
