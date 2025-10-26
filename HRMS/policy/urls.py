from django.urls import path
from .views import (
    LeavePolicyListCreateView,
    LeavePolicyDetailView,
    LeavePolicyMeView,
    LeavePolicySafeLookupView,
    LeavePolicyHistoryView  
)

urlpatterns = [
    # List + Create (Superadmin & HR)
    path("policies/", LeavePolicyListCreateView.as_view(), name="policy-list-create"),

    # Detail view (UUID) — for Superadmin & HR
    path("policies/<uuid:pk>/", LeavePolicyDetailView.as_view(), name="policy-detail"),

    # Employee & HR view of their org’s active policies
    path("policies/myorg/", LeavePolicyMeView.as_view(), name="policy-myorg"),

    # NEW: Safe lookup with friendly 404 (Superadmin & HR only)
    path("policies/safe/<uuid:pk>/", LeavePolicySafeLookupView.as_view(), name="policy-safe-detail"),

    path("policies/history/", LeavePolicyHistoryView.as_view(), name="policy-history"),

]
