from rest_framework import generics, permissions
from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationPermission(permissions.BasePermission):
    """
    Unified permission for organization access:
    - SuperAdmin → can create, update, delete, view all
    - HR, Employee → can only view their own organization
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Allow read-only access to everyone logged in
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only SuperAdmin can modify organizations
        return request.user.role == "SUPERADMIN"


class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, OrganizationPermission]

    def get_queryset(self):
        user = self.request.user
        # SuperAdmin sees all
        if user.role == "SUPERADMIN":
            return Organization.objects.all()
        # HR & Employee see only their own
        return Organization.objects.filter(id=user.organization.id)


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, OrganizationPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPERADMIN":
            return Organization.objects.all()
        return Organization.objects.filter(id=user.organization.id)
