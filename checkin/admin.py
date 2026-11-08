from django.contrib import admin

from .models import CheckInOut


@admin.register(CheckInOut)
class CheckInOutAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "check_in", "check_out")
    list_filter = ("date",)
    search_fields = ("user__username",)
    date_hierarchy = "date"
