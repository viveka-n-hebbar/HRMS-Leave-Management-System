from django.urls import path
from .views import LeaveListCreateView, LeaveDetailView, LeaveMeView

urlpatterns = [
    path("leaves/", LeaveListCreateView.as_view(), name="leave-list-create"),
    path("leaves/<uuid:pk>/", LeaveDetailView.as_view(), name="leave-detail"),
    path("leaves/me/", LeaveMeView.as_view(), name="leave-me"),
]
