from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'employee_code', 'department', 'designation', 'organization', 'is_active')
    list_filter = ('organization', 'department', 'is_active')
