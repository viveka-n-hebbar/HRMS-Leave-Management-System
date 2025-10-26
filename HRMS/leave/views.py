from datetime import date
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Leave
from .serializers import LeaveSerializer
from employee.models import Employee
from django.db.models import F, Sum, ExpressionWrapper, DurationField
from datetime import date, timedelta


class LeavePermission(permissions.BasePermission):
    """
    Permissions for Leave model:
    - SUPERADMIN → Full CRUD
    - HR → CRUD within their organization
    - EMPLOYEE → Create + Read own (via /leaves/me/ api endpoint)
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # All authenticated users can read their own
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow create for Employee + HR + SUPERADMIN
        return user.role in ["SUPERADMIN", "HR", "EMPLOYEE"]

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == "SUPERADMIN":
            return True
        if user.role == "HR" and obj.organization == user.organization:
            return True
        if user.role == "EMPLOYEE" and obj.user == user:
            return request.method in ["GET", "POST"]
        return False



# List + Create Leaves
class LeaveListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated, LeavePermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == "SUPERADMIN":
            return Leave.objects.all()
        elif user.role == "HR":
            return Leave.objects.filter(organization=user.organization)
        elif user.role == "EMPLOYEE":
            # Employees can only see their own leaves in /leaves/me/
            return Leave.objects.none()
        return Leave.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        employee = get_object_or_404(Employee, user=user)
        policy = serializer.validated_data.get("policy")

        if not policy:
            raise PermissionDenied("A valid leave policy must be selected.")

        # 1️Policy must be active
        if not policy.is_active:
            raise PermissionDenied("This leave policy is not active.")

        start_date = serializer.validated_data.get("start_date")
        end_date = serializer.validated_data.get("end_date")
        days_requested = (end_date - start_date).days + 1

        # 2️Notice period validation
        today = date.today()
        if (start_date - today).days < policy.notice_period_days:
            raise PermissionDenied(
                f"Leave must be applied at least {policy.notice_period_days} days in advance."
            )

        # 3️Document requirement
        attachment = serializer.validated_data.get("attachment")
        if policy.requires_document and days_requested > policy.max_days_without_doc and not attachment:
            raise PermissionDenied(
                f"This leave type requires a supporting document for more than {policy.max_days_without_doc} days."
            )

        # 4️Max days per year validation
        year_start = date(today.year, 1, 1)
        year_end = date(today.year, 12, 31)

        # Calculate total approved leave days for that employee and policy in the year
        total_taken = (
            Leave.objects.filter(
                employee=employee,
                policy=policy,
                status="Approved",
                start_date__gte=year_start,
                end_date__lte=year_end
            )
            .annotate(days=ExpressionWrapper(F('end_date') - F('start_date') + timedelta(days=1), output_field=DurationField()))
            .aggregate(total=Sum('days'))
            .get('total')
        )

        total_taken_days = total_taken.days if total_taken else 0

        if total_taken_days + days_requested > policy.max_days_per_year:
            raise PermissionDenied(
                f"Cannot apply {days_requested} days. You have already used {total_taken_days}/{policy.max_days_per_year} days this year."
            )

        # If all validations pass → save leave
        serializer.save(
            organization=employee.organization,
            employee=employee,
            user=user,
            status="Pending"
        )

# Employee’s Own Leave History (/leaves/me/)
class LeaveMeView(generics.ListAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Leave.objects.filter(user=user).order_by("-created_at")


# Retrieve, Update (Approve/Reject/Cancel), Delete (for HR & SUPERADMIN)
class LeaveDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated, LeavePermission]
    queryset = Leave.objects.all()

    def get_object(self):
        user = self.request.user
        pk = self.kwargs.get("pk")

        leave = get_object_or_404(Leave, pk=pk)

        # EMPLOYEE cannot access /leaves/<uuid>/ directly
        if user.role == "EMPLOYEE":
            raise PermissionDenied({"detail": "You are not allowed to access leave by UID."})

        # HR and SUPERADMIN access
        if user.role == "SUPERADMIN":
            return leave
        if user.role == "HR" and leave.organization == user.organization:
            return leave

        raise PermissionDenied({"detail": "Not authorized to view this record."})

    def update(self, request, *args, **kwargs):
        user = request.user
        leave = self.get_object()

        if user.role not in ["SUPERADMIN", "HR"]:
            raise PermissionDenied("You cannot approve or reject leave requests.")

        action = request.data.get("action")
        remarks = request.data.get("remarks", "")

        if action not in ["approve", "reject", "cancel"]:
            return Response(
                {"detail": "Invalid action. Use 'approve', 'reject', or 'cancel'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update leave status
        if action == "approve":
            leave.status = "Approved"
        elif action == "reject":
            leave.status = "Rejected"
        elif action == "cancel":
            leave.status = "Cancelled"

        leave.reviewed_by = user
        leave.remarks = remarks
        leave.save()

        serializer = self.get_serializer(leave)
        return Response(serializer.data, status=status.HTTP_200_OK)
