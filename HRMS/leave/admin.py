from django.contrib import admin
from .models import Leave

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "organization",
        "policy",
        "start_date",
        "end_date",
        "status",
        "created_at",
    )
    list_filter = ("status", "organization", "policy")
    search_fields = ("employee__user__email", "reason")
