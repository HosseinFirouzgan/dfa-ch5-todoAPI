from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

User = get_user_model()


# Create your tests here.
class RegisterViewTests(APITestCase):

    def test_user_can_register(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "email": "test@mail.com",
                "password": "testpass123",
                "password2": "testpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@mail.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_password_is_not_returned(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "email": "test@mail.com",
                "password": "testpass123",
                "password2": "testpass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertNotIn("password2", response.data)

    def test_user_cannot_register_with_duplicate_username(self):
        User.objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )

        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "email": "alice@gmail.com",
                "password": "testpass123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)


class LoginViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "supernatural123"
        cls.user = User.objects.create_user(
            username="DeanWinchester",
            email="purgatory@divine.com",
            password=cls.password,
        )

    def test_user_can_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], self.user.username)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_user_can_not_login_with_invalid_pass(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": "invalid_password"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_user_can_not_login_with_invalid_username(self):
        response = self.client.post(
            reverse("login"),
            {"username": "invalid_username", "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_nothing_more_is_returned_after_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertNotIn("password", response.data["user"])
        self.assertNotIn("is_staff", response.data["user"])
        self.assertNotIn("last_login", response.data["user"])
        self.assertNotIn("is_superuser", response.data["user"])

    def test_username_is_required_for_login(self):
        response = self.client.post(
            reverse("login"),
            {"password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_required_for_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "testpass123"
        cls.user = User.objects.create_user(
            username="sam_winchester",
            email="life@hunting.com",
            password=cls.password,
        )

    def test_authenticated_user_can_logout(self):
        login_reponse = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )
        refresh = login_reponse.data["refresh"]
        access = login_reponse.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(
            reverse("logout"),
            {"refresh": refresh, "access": access},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_blacklisted_refresh_token_cannot_be_used_again(self):
        pass
