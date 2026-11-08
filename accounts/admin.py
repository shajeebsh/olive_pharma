from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "employee_code", "region")
    list_filter = ("role", "region")
    search_fields = ("user__username", "user__first_name", "user__last_name", "employee_code")
