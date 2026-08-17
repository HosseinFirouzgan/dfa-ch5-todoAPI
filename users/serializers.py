from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],  # enforces Django's Auth_PASSWORD_VALIDATORS
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"passwords": "passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        validated_data["email"] = validated_data["email"].lower()
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


# notice that this is not a model serializer.
# It simply validating and processing data
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)  # this field is input only

    def save(self):
        try:
            refresh_token = self.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError(
                {"refresh": "Invalid or expired refresh token."}
            )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user

        # check old_password
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": ["old password is incorrect"]}
            )

        # check passwords match
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": ["passwords do not match"]}
            )

        # prevent using the same password for the new one
        # if attrs["old_password"] == attrs["new_password"]:
        if user.check_password(attrs["new_password"]):
            raise serializers.ValidationError(
                {"new_password": ["New password is the same as the old one."]}
            )

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user

        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])

        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        email = self.validated_data["email"]

        user = User.objects.filter(email=email).first()

        # if the user does not exist the serializer exits silently with no exceptions raised
        if not user:
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))

        token = default_token_generator.make_token(user)

        reset_url = (
            f"https://localhost:8000/api/users/password-reset/confirm/"
            f"{uid}/{token}/"
        )

        send_mail(
            subject="Password Reset",
            message=(
                "use the following link to reset your password\n\n" f"{reset_url}"
            ),
            from_email="noreply@todo.list",
            recipient_list=[user.email],
        )
