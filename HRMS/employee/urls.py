from django.urls import path
from .views import EmployeeListCreateView, EmployeeDetailView, EmployeeMeView

urlpatterns = [
    path("employees/", EmployeeListCreateView.as_view(), name="employee-list-create"),
    path("employees/me/", EmployeeMeView.as_view(), name="employee-me"),
    path("employees/<uuid:pk>/", EmployeeDetailView.as_view(), name="employee-detail"),
]
