from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Employee
from .serializers import EmployeeSerializer


class EmployeePermission(permissions.BasePermission):
    """
    Permission control for Employee model:
    - SUPERADMIN → Full CRUD
    - HR → CRUD within their organization
    - EMPLOYEE → Read-only (self)
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return user.role in ["SUPERADMIN", "HR"]

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "SUPERADMIN":
            return True
        if user.role == "HR" and obj.organization == user.organization:
            return True
        if user.role == "EMPLOYEE" and obj.user == user and request.method in permissions.SAFE_METHODS:
            return True
        return False


# List + Create Employees
class EmployeeListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, EmployeePermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPERADMIN":
            return Employee.objects.all()
        elif user.role == "HR":
            return Employee.objects.filter(organization=user.organization)
        elif user.role == "EMPLOYEE":
            return Employee.objects.filter(user=user)
        return Employee.objects.none()

    def perform_create(self, serializer):
      user = self.request.user

      # get user_id from request.data
      user_id = self.request.data.get("user")

      if not user_id:
          raise PermissionDenied("User field is required to create an employee.")

      if user.role == "HR":
          serializer.save(user_id=user_id, organization=user.organization)
      elif user.role == "SUPERADMIN":
          serializer.save(user_id=user_id)
      else:
          raise PermissionDenied("You do not have permission to create employees.")

# Get, Update, or Delete employee by UUID
class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, EmployeePermission]
    queryset = Employee.objects.all()

    def get_object(self):
        user = self.request.user
        pk = self.kwargs.get("pk")

        # If not found → 404, not crash
        employee = get_object_or_404(Employee, pk=pk)

        # Role-based access control
        if user.role == "SUPERADMIN":
            return employee
        if user.role == "HR" and employee.organization == user.organization:
            return employee
        if user.role == "EMPLOYEE" and employee.user == user:
            return employee

        raise PermissionDenied({"detail": "You are not authorized to access this employee record."})


# Get logged-in employee’s own profile
class EmployeeMeView(generics.RetrieveAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Get the employee record linked to the logged-in user
        return get_object_or_404(Employee, user=self.request.user)
