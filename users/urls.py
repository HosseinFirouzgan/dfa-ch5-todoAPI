from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    LoginView,
    PasswordChangeView,
    ProfileView,
    RegisterView,
    LogoutView,
    PasswordResetView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", PasswordChangeView.as_view(), name="password_change"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
]
