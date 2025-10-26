from django.contrib import admin
from .models import LeavePolicy, LeavePolicyHistory


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "policy_type",
        "organization",
        "max_days_per_year",
        "carry_forward_days",
        "requires_document",
        "is_active",
        "created_by",
        "updated_at",
    )
    list_filter = ("organization", "is_active", "policy_type")
    search_fields = ("name", "organization__name")
    readonly_fields = ("created_by", "updated_at")
    ordering = ("-updated_at",)


@admin.register(LeavePolicyHistory)
class LeavePolicyHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for tracking changes to Leave Policies.
    Displays who changed what and when, and stores full text snapshots.
    """
    list_display = (
        "policy",
        "version_number",
        "changed_by",
        "changed_at",
    )
    list_filter = ("policy__organization", "changed_by")
    search_fields = ("policy__name", "changed_by__username")
    readonly_fields = (
        "policy",
        "version_number",
        "policy_snapshot",
        "changed_by",
        "changed_at",
    )
    ordering = ("-changed_at",)

    def has_add_permission(self, request):
        # Prevent manual addition — history is automatically recorded
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent editing of history records
        return False
