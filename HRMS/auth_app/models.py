from django.db import models
from django.contrib.auth.models import AbstractUser
from organization.models import Organization

class User(AbstractUser):
    ROLE_CHOICES = (
        ('SUPERADMIN', 'Super Admin'),
        ('HR', 'HR Manager'),
        ('EMPLOYEE', 'Employee'),
    )

    # Login will use email instead of username
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Only SUPERADMIN can have no organization
        if self.role != 'SUPERADMIN' and self.organization is None:
            raise ValueError("Only SUPERADMIN can exist without an organization.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
