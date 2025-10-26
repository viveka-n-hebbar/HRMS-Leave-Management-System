from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'organization', 'is_staff', 'is_active')
    list_filter = ('role', 'organization')
