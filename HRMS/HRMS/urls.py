from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # existing urls...
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #all app urls below
    path('api/auth/', include('auth_app.urls')),
    path('organization/', include('organization.urls')),
    path('', include('employee.urls')),
    path('', include('policy.urls')),
    path('', include('leave.urls')),
]
