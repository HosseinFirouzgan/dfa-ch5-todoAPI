from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


# Create your tests here.
class RegisterViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="hossein",
            email="hossein@mail.com",
            password="StrongPass123",
            # password2="StrongPass123",
        )

    def test_user_can_register(self):

        response = self.client.post(
            reverse("register"),
            {
                "username": self.user.username,
                "email": self.user.email,
                "password": self.user.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username="hossein")
        self.assertEqual(user.email, "hossein@mail.com")
        self.assertTrue(user.check_password("StrongPass123"))

    def test_password_is_not_returned(self):
        pass
