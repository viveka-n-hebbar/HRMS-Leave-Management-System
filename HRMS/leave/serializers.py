from rest_framework import serializers
from .models import Leave

class LeaveSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    employee_name = serializers.CharField(source='employee.user.username', read_only=True)
    employee_email = serializers.EmailField(source='employee.user.email', read_only=True)
    employee_role = serializers.CharField(source='employee.user.role', read_only=True)
    policy_name = serializers.CharField(source='policy.name', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True, default=None)

    class Meta:
        model = Leave
        fields = [
            'id', 'organization', 'organization_name',
            'employee', 'employee_name', 'employee_email', 'employee_role',
            'user', 'policy', 'policy_name',
            'start_date', 'end_date', 'reason', 'attachment',
            'status', 'remarks', 'reviewed_by', 'reviewed_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'employee', 'user',
            'status', 'reviewed_by', 'created_at', 'updated_at'
        ]
