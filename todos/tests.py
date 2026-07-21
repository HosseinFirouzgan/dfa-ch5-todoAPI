from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Todo

User = get_user_model()


# Create your tests here.
class TodoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="boby",
            password="testpass123",
        )
        cls.other_user = User.objects.create_user(
            username="Castiel",
            password="testpass123",
        )
        cls.todo = Todo.objects.create(
            user=cls.user,
            title="test todo",
            body="something that explains what needs to be done",
        )
        cls.other_todo = Todo.objects.create(
            user=cls.other_user,
            title="watch supernatural",
            body="watch then buy an Implala",
        )

    def authenticate(self, user):
        response = self.client.post(
            reverse("token_obtain_pain"),
            {"username": user.username, "password": "testpass123"},
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_model_content(self):
        self.assertEqual(self.todo.title, "test todo")
        self.assertEqual(
            self.todo.body, "something that explains what needs to be done"
        )
        self.assertEqual(str(self.todo), "test todo")

    def test_list_requires_authentication(self):
        response = self.client.get(reverse("todo-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_listview(self):
        response = self.client.get(reverse("todo_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Todo.objects.count(), 1)
        self.assertContains(response, self.todo)

    def test_api_detailview(self):
        response = self.client.get(
            reverse("todo_detail", kwargs={"pk": self.todo.id}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Todo.objects.count(), 1)
        self.assertContains(response, "test todo")
