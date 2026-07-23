from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Todo

User = get_user_model()


class TodoAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="alice",
            email="alice@mail.com",
            password="testpass123",
            # password2="testpass123",
        )
        cls.other_user = User.objects.create_user(
            username="bob",
            email="bob@mail.com",
            password="testpass123",
            # password2="testpass123",
        )

        cls.todo = Todo.objects.create(
            user=cls.user,
            title="test todo",
            body="something that explains what needs to be done",
        )
        cls.other_todo = Todo.objects.create(
            user=cls.other_user,
            title="bob's todo",
            body="bob's private task",
        )

    def authenticate(self, user):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": user.username, "password": "testpass123"},
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_model_content(self):
        self.assertEqual(self.todo.title, "test todo")
        self.assertEqual(str(self.todo), "test todo")

    def test_list_requires_authentication(self):
        response = self.client.get(reverse("todo-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_returns_own_todos(self):
        self.authenticate(self.user)
        response = self.client.get(reverse("todo-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [todo["title"] for todo in response.data]
        self.assertIn("test todo", titles)
        self.assertNotIn("bob's todo", titles)

    def test_detail_view(self):
        self.authenticate(self.user)
        response = self.client.get(reverse("todo-detail", kwargs={"pk": self.todo.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "test todo")

    def test_cannot_access_another_users_todo(self):
        self.authenticate(self.user)
        response = self.client.get(
            reverse("todo-detail", kwargs={"pk": self.other_todo.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_todo_assigns_current_user(self):
        self.authenticate(self.user)
        response = self.client.post(
            reverse("todo-list"), {"title": "new task", "body": "details"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Todo.objects.get(id=response.data["id"])
        self.assertEqual(created.user, self.user)
