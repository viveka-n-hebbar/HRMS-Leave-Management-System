from django.contrib import admin
from .models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'timezone', 'created_at')
    search_fields = ('name', 'code')
