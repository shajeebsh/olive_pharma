from django.contrib import admin

from .models import SalesLog, Target


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = (
        "rep",
        "period",
        "start_date",
        "end_date",
        "product",
        "amount_target",
        "quantity_target",
    )
    list_filter = ("period", "start_date")
    search_fields = ("rep__username", "product__name")


@admin.register(SalesLog)
class SalesLogAdmin(admin.ModelAdmin):
    list_display = (
        "rep",
        "sales_date",
        "product",
        "quantity",
        "amount",
        "pharmacy",
        "entered_by",
    )
    list_filter = ("sales_date", "region", "product")
    search_fields = ("rep__username", "reference", "pharmacy__name")
    date_hierarchy = "sales_date"
