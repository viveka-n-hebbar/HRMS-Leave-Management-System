# policy/views.py
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, NotFound
from django.shortcuts import get_object_or_404
from .models import LeavePolicy, LeavePolicyHistory
from .serializers import LeavePolicySerializer, LeavePolicyHistorySerializer

# PERMISSIONS
class LeavePolicyPermission(permissions.BasePermission):
    """
    Access control:
    - SUPERADMIN → all
    - HR → their organization
    - EMPLOYEE → read-only (their org)
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # safe methods allowed if authenticated
        if request.method in permissions.SAFE_METHODS:
            return True
        # write operations only for SUPERADMIN and HR
        return user.role in ["SUPERADMIN", "HR"]

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "SUPERADMIN":
            return True
        if user.role == "HR" and obj.organization == user.organization:
            return True
        if user.role == "EMPLOYEE" and obj.organization == user.organization and request.method in permissions.SAFE_METHODS:
            return True
        return False


# Helpers
def build_policy_snapshot_text(policy_instance, changed_by_user=None):
    """
    Build a readable text snapshot for the policy_instance.
    This ensures we don't store model objects in DB and avoid serialization errors.
    """
    return (
        f"Name: {policy_instance.name}\n"
        f"Type: {policy_instance.policy_type}\n"
        f"Description: {policy_instance.description or ''}\n"
        f"Organization: {policy_instance.organization.name if policy_instance.organization else 'N/A'}\n"
        f"Max Days/Year: {policy_instance.max_days_per_year}\n"
        f"Carry Forward Days: {policy_instance.carry_forward_days}\n"
        f"Requires Document: {policy_instance.requires_document}\n"
        f"Max Days Without Doc: {policy_instance.max_days_without_doc}\n"
        f"Notice Period Days: {policy_instance.notice_period_days}\n"
        f"Allow Encashment: {policy_instance.allow_encashment}\n"
        f"Encashment Limit: {policy_instance.encashment_limit}\n"
        f"Is Active: {policy_instance.is_active}\n"
        f"Updated At: {policy_instance.updated_at}\n"
        f"Changed By: {changed_by_user.email if changed_by_user else 'N/A'}\n"
    )



# LIST + CREATE

class LeavePolicyListCreateView(generics.ListCreateAPIView):
    serializer_class = LeavePolicySerializer
    permission_classes = [permissions.IsAuthenticated, LeavePolicyPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPERADMIN":
            return LeavePolicy.objects.all()
        elif user.role in ["HR", "EMPLOYEE"]:
            return LeavePolicy.objects.filter(organization=user.organization)
        return LeavePolicy.objects.none()

    def perform_create(self, serializer):
        """
        Create the policy and an initial history snapshot (version 1).
        """
        user = self.request.user

        if user.role == "HR":
            instance = serializer.save(organization=user.organization, created_by=user)
        elif user.role == "SUPERADMIN":
            instance = serializer.save(created_by=user)
        else:
            raise PermissionDenied("You do not have permission to create leave policies.")

        # create initial snapshot as text
        snapshot_text = build_policy_snapshot_text(instance, changed_by_user=user)

        LeavePolicyHistory.objects.create(
            policy=instance,
            version_number=1,
            policy_snapshot=snapshot_text,
            changed_by=user
        )


# DETAIL (UUID-based) with safe 404 + history tracking
class LeavePolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LeavePolicySerializer
    permission_classes = [permissions.IsAuthenticated, LeavePolicyPermission]
    queryset = LeavePolicy.objects.all()

    def get_object(self):
        user = self.request.user
        policy_id = self.kwargs.get("pk")

        try:
            policy = LeavePolicy.objects.get(pk=policy_id)
        except LeavePolicy.DoesNotExist:
            raise NotFound({"detail": f"No matching Leave Policy found for UID: {policy_id}"})

        if user.role == "SUPERADMIN":
            return policy
        if user.role == "HR" and policy.organization == user.organization:
            return policy

        raise PermissionDenied("You are not authorized to access this policy.")

    def perform_update(self, serializer):
        """
        Save update and create a history entry with a readable snapshot.
        """
        user = self.request.user
        instance = serializer.save()

        snapshot_text = build_policy_snapshot_text(instance, changed_by_user=user)
        LeavePolicyHistory.objects.create(
            policy=instance,
            version_number=instance.history.count() + 1,
            policy_snapshot=snapshot_text,
            changed_by=user
        )


# EMPLOYEE / HR view for their org’s active policies (/policies/myorg/)
class LeavePolicyMeView(generics.ListAPIView):
    serializer_class = LeavePolicySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["EMPLOYEE", "HR"]:
            return LeavePolicy.objects.filter(organization=user.organization, is_active=True)
        elif user.role == "SUPERADMIN":
            return LeavePolicy.objects.filter(is_active=True)
        return LeavePolicy.objects.none()


# SAFE UID LOOKUP VIEW
class LeavePolicySafeLookupView(generics.RetrieveAPIView):
    """
    Safely returns a policy by UID with 404 handling.
    Accessible only to SUPERADMIN and HR.
    """
    serializer_class = LeavePolicySerializer
    permission_classes = [permissions.IsAuthenticated, LeavePolicyPermission]

    def get_object(self):
        user = self.request.user
        policy_id = self.kwargs.get("pk")

        try:
            policy = LeavePolicy.objects.get(pk=policy_id)
        except LeavePolicy.DoesNotExist:
            raise NotFound({"detail": f"No Leave Policy found with UID: {policy_id}"})

        if user.role in ["SUPERADMIN", "HR"] and (
            user.role == "SUPERADMIN" or policy.organization == user.organization
        ):
            return policy

        raise PermissionDenied("You are not authorized to access this policy.")


# HISTORY VIEW (NO PK REQUIRED)
class LeavePolicyHistoryView(generics.ListAPIView):
    """
    Shows all policy history:
      - SUPERADMIN → all organizations
      - HR/EMPLOYEE → only their organization's policies
    """
    serializer_class = LeavePolicyHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "SUPERADMIN":
            return LeavePolicyHistory.objects.select_related("policy", "changed_by").all()

        elif user.role in ["HR", "EMPLOYEE"]:
            return LeavePolicyHistory.objects.filter(
                policy__organization=user.organization
            ).select_related("policy", "changed_by")

        return LeavePolicyHistory.objects.none()
