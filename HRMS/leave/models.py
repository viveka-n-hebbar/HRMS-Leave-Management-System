import uuid
from django.db import models
from organization.models import Organization
from policy.models import LeavePolicy
from auth_app.models import User
from employee.models import Employee 

class Leave(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="leaves"
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leaves"
    )
    user = models.ForeignKey(  # the account who applied (linked to Employee.user)
        User, on_delete=models.CASCADE, related_name="leave_user"
    )
    policy = models.ForeignKey(
        LeavePolicy, on_delete=models.SET_NULL, null=True, blank=True, related_name="leaves"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()

    # optional supporting document (medical proof, travel proof, etc.)
    attachment = models.FileField(upload_to="leave_attachments/", null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    remarks = models.TextField(blank=True, null=True)

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leave"
        verbose_name = "Leave"
        verbose_name_plural = "Leaves"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.user.email} | {self.policy.name if self.policy else 'No Policy'} ({self.status})"
