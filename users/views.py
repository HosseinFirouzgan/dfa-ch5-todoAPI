from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response

from .serializers import LogoutSerializer, RegisterSerializer, LoginSerializer

User = get_user_model()


# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can signup no tokens needed


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "successfully logged out"},
            status=status.HTTP_205_RESET_CONTENT,
        )
