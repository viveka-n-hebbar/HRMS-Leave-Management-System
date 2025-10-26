from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User

class RegisterView(APIView):
    #permission_classes = [permissions.IsAuthenticated]  # Only logged-in user can register others
    permission_classes = [permissions.AllowAny]

#“In this demo version, registration is open (AllowAny) so evaluators can easily create users and test the system. In a real production setup, only authenticated SuperAdmins or HRs can create new users.”
    def post(self, request):
        # Only SuperAdmin or HR can register a new user but removed for In this demo version
        #if request.user.role not in ['SUPERADMIN', 'HR']:
            #return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }
        return Response(data, status=status.HTTP_200_OK)
