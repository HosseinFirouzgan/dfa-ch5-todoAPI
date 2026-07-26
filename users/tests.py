from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
            password2="testpass123",
        )

        response = self.client.post(
            reverse("register"),
            {
                "username": "testuser",
                "email": "alice@gmail.com",
                "password": "testpass123",
                "password2": "testpass123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
