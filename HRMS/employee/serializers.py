from rest_framework import serializers
from .models import Employee
from auth_app.models import User


class EmployeeSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'username', 'user_email', 'user_role',
            'organization', 'employee_code', 'department',
            'designation', 'date_of_joining', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']  #Added 'user' here
