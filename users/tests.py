from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

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

        # login
        login_response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        # print(login_response.data)

        # logout
        refresh = login_response.data["refresh"]
        access = login_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_response = self.client.post(
            reverse("logout"),
            {"refresh": refresh},
        )
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        # refresh token
        refresh_response = self.client.post(
            reverse("token_refresh"),
            {"refresh": refresh},
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_logout(self):
        response = self.client.post(
            reverse("logout"),
            {"refresh": "dummy token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordChangeViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.old_password = "Underworldemon123"
        cls.user = User.objects.create_user(
            username="crowly",
            email="crowlytheking@hell.com",
            password=cls.old_password,
        )
        cls.new_password = "NewKing123"

    def authenticate(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.old_password},
        )

        access = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_change_password(self):
        self.authenticate()

        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "new_password2": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))  # new pass works
        self.assertFalse(
            self.user.check_password(self.old_password)
        )  # old pass does'nt work

    def test_wrong_old_password_get_rejected(self):
        self.authenticate()

        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": "wrong-pass",
                "new_password": self.new_password,
                "new_password2": self.new_password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

    def test_new_passwords_must_match(self):
        self.authenticate()

        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "new_password2": "something_different",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password2", response.data)

    def test_weak_password_gets_rejected(self):
        self.authenticate()

        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": self.old_password,
                "new_password": "123456",
                "new_password2": "123456",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_anonymous_user_cannot_change_password(self):

        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "new_password2": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_new_password_cannot_be_same_as_old_password(self):
        self.authenticate()

        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": self.old_password,
                "new_password": self.old_password,
                "new_password2": self.old_password,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.password = "impala123"
        cls.user = User.objects.create_user(
            username="supernatural_fan",
            email="fan@gmail.com",
            password=cls.password,
        )

    def authenticate(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": self.user.username,
                "email": self.user.email,
                "password": self.password,
                "password2": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data["access"]}")

    def test_authenticated_user_can_get_profile(self):
        self.authenticate()

        response = self.client.get(reverse("profile"))
        # print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)

    def test_anonymous_user_cannot_get_profile(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.password = "testpass123"
        cls.user = User.objects.create_user(
            email="testuser@mail.com",
            username="testuser",
            password=cls.password,
        )

    def test_password_reset_email_is_sent(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": self.user.email},
            format="json",
        )

        # print(list(mail.outbox))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(
            email.to,
            [self.user.email],
        )

        self.assertIn("Password Reset", email.subject)

        # uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        # token = default_token_generator.make_token(self.user)

        self.assertIn("uid=", email.body)
        self.assertIn("token=", email.body)

    def test_unknown_email_returns_success(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "wrongemail@notmail.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("email", response.data["detail"])

    def test_invalid_email_is_rejected(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "notanemail"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class PasswordResetConfirmViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.old_password = "olddemon123"
        cls.new_password = "newking123"

        cls.user = User.objects.create_user(
            username="crowly",
            email="crowlytheking@hell.com",
            password=cls.old_password,
        )

    def get_reset_data(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        return uid, token

    def test_user_can_change_password_with_token(self):
        uid, token = self.get_reset_data()

        response = self.client.post(
            reverse("password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": self.new_password,
                "new_password2": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))
        self.assertFalse(self.user.check_password(self.old_password))

    def test_invalid_token_is_rejected(self):
        uid, token = self.get_reset_data()

        response = self.client.post(
            reverse("password_reset_confirm"),
            {
                "uid": uid,
                "token": "invalid token",
                "new_password": self.new_password,
                "new_password2": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_uid_is_rejected(self):
        uid, token = self.get_reset_data()

        response = self.client.post(
            reverse("password_reset_confirm"),
            {
                "uid": "invalid uid",
                "token": token,
                "new_password": self.new_password,
                "new_password2": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_passwords_must_match(self):
        uid, token = self.get_reset_data()

        response = self.client.post(
            reverse("password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": self.new_password,
                "new_password2": "lucifertheking123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password2", response.data)

    def test_weak_password_gets_rejected(self):
        uid, token = self.get_reset_data()

        response = self.client.post(
            reverse("password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": "123456",
                "new_password2": "123456",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_token_cannot_be_reused(self):
        uid, token = self.get_reset_data()

        response = self.client.post(
            reverse("password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": self.new_password,
                "new_password2": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        duplicate_response = self.client.post(
            reverse("password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": self.new_password,
                "new_password2": self.new_password,
            },
            format="json",
        )

        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
