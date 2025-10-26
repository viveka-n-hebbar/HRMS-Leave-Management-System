# policy/serializers.py
from rest_framework import serializers
from .models import LeavePolicy
from .models import LeavePolicyHistory


class LeavePolicySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_role = serializers.CharField(source='created_by.role', read_only=True)

    class Meta:
        model = LeavePolicy
        fields = [
            'id', 'organization', 'organization_name',
            'name', 'policy_type', 'description',
            'max_days_per_year', 'carry_forward_days',
            'requires_document', 'max_days_without_doc',
            'notice_period_days', 'allow_encashment',
            'encashment_limit', 'is_active',
            'created_by', 'created_by_username', 'created_by_email', 'created_by_role',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def validate(self, data):
        policy_type = data.get("policy_type")
        max_days = data.get("max_days_per_year", 0)
        requires_doc = data.get("requires_document", False)
        max_days_without_doc = data.get("max_days_without_doc", 0)
        notice = data.get("notice_period_days", 0)
        allow_encash = data.get("allow_encashment", False)
        encash_limit = data.get("encashment_limit", 0)

        # 1️ Annual Leave validations
        if policy_type == "ANNUAL":
            if not allow_encash:
                raise serializers.ValidationError(
                    {"allow_encashment": "Annual leave must allow encashment as per policy."}
                )
            if encash_limit <= 0:
                raise serializers.ValidationError(
                    {"encashment_limit": "Please specify a valid encashment limit for Annual Leave."}
                )
            if not (10 <= max_days <= 30):
                raise serializers.ValidationError(
                    {"max_days_per_year": "Annual leave entitlement must be between 10 and 30 days."}
                )

        # 2️Sick Leave validations
        elif policy_type == "SICK":
            if max_days_without_doc > 3:
                raise serializers.ValidationError(
                    {"max_days_without_doc": "Sick Leave cannot allow more than 3 days without documentation."}
                )
            if max_days > 15:
                raise serializers.ValidationError(
                    {"max_days_per_year": "Sick Leave cannot exceed 15 days per year."}
                )

        # 3️ Casual Leave validations
        elif policy_type == "CASUAL":
            if max_days > 12:
                raise serializers.ValidationError(
                    {"max_days_per_year": "Casual Leave cannot exceed 12 days per year."}
                )
            if data.get("carry_forward_days", 0) > 0:
                raise serializers.ValidationError(
                    {"carry_forward_days": "Casual Leave cannot be carried forward."}
                )
            if allow_encash:
                raise serializers.ValidationError(
                    {"allow_encashment": "Encashment is not allowed for Casual Leave."}
                )

        # 4️ Unpaid Leave validations
        elif policy_type == "UNPAID":
            if max_days > 365:
                raise serializers.ValidationError(
                    {"max_days_per_year": "Unpaid leave should not exceed 365 days."}
                )

        # 5️ Common validation — notice period
        if notice > 30:
            raise serializers.ValidationError(
                {"notice_period_days": "Notice period cannot exceed 30 days."}
            )

        return data

class LeavePolicyHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(source="changed_by.email", read_only=True)
    policy_name = serializers.CharField(source="policy.name", read_only=True)
    policy_type = serializers.CharField(source="policy.policy_type", read_only=True)

    class Meta:
        model = LeavePolicyHistory
        fields = [
            "id",
            "policy",
            "policy_name",
            "policy_type",
            "version_number",
            "policy_snapshot",
            "changed_by",
            "changed_by_email",
            "changed_at",
        ]
        read_only_fields = ["id", "changed_at"]
