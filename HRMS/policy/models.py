import uuid
from django.db import models
from django.conf import settings
from organization.models import Organization
from django.db import models
from django.conf import settings

class LeavePolicy(models.Model):
    POLICY_TYPES = [
        ("ANNUAL", "Annual Leave"),
        ("SICK", "Sick Leave"),
        ("CASUAL", "Casual Leave"),
        ("UNPAID", "Unpaid Leave"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="leave_policies"
    )
    name = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES)
    description = models.TextField(blank=True)

    # Key leave rules
    max_days_per_year = models.PositiveIntegerField(default=0)
    carry_forward_days = models.PositiveIntegerField(default=0)
    requires_document = models.BooleanField(default=False)
    max_days_without_doc = models.PositiveIntegerField(default=0)
    notice_period_days = models.PositiveIntegerField(default=0)
    allow_encashment = models.BooleanField(default=False)
    encashment_limit = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_policies"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leave_policy"
        verbose_name = "Leave Policy"
        verbose_name_plural = "Leave Policies"
        unique_together = ("organization", "name", "policy_type")

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.policy_type})"


class LeavePolicyHistory(models.Model):
    policy = models.ForeignKey('LeavePolicy', on_delete=models.CASCADE, related_name='history')
    version_number = models.PositiveIntegerField(default=1)

    # Store readable snapshot instead of JSON (no serialization issues)
    policy_snapshot = models.TextField()  

    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.policy.name} (v{self.version_number})"
