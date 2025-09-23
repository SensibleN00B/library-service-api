from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.test import APITestCase

from books.models import Book
from books.serializers import BookSerializer


class BookModelTest(TestCase):

    def test_str_method(self):
        book = Book.objects.create(
            title="Test Book",
            author="Serhii Developer",
            daily_fee=5.0,
            inventory=10,
        )
        self.assertEqual(str(book), "Test Book by Serhii Developer")

    def test_inventory_positive(self):
        book = Book(title="Book", author="Author", daily_fee=5.0, inventory=10)
        book.save()
        self.assertGreaterEqual(book.inventory, 0)

    def test_daily_fee_constraint(self):
        book = Book(title="Book", author="Author", daily_fee=0, inventory=1)
        with self.assertRaises(IntegrityError):
            book.save()


User = get_user_model()


class BookAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="pass"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="pass"
        )
        self.book = Book.objects.create(
            title="Original Book", author="Author", inventory=5, daily_fee=3.0
        )
        self.list_url = reverse("books:book-list")

    def test_list_requires_authentication(self):
        """Unauthenticated users cannot list books"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated_user(self):
        """Authenticated users can list books"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_book(self):
        """Retrieve a book detail"""
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-detail", args=[self.book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book.title)

    def test_create_book_admin_only(self):
        """Only admin can create a book"""
        self.client.force_authenticate(user=self.admin)
        payload = {
            "title": "New Book",
            "author": "Author",
            "inventory": 2,
            "daily_fee": 5.0,
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_book_non_admin_forbidden(self):
        """Non-admin users cannot create a book"""
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "New Book",
            "author": "Author",
            "inventory": 2,
            "daily_fee": 5.0,
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_admin_only(self):
        """Admin can update book"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("books:book-detail", args=[self.book.id])
        payload = {
            "title": "Updated Title",
            "author": "Author",
            "inventory": 5,
            "daily_fee": 3.0,
        }
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Title")

    def test_partial_update_book_admin_only(self):
        """Admin can partially update book"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("books:book-detail", args=[self.book.id])
        payload = {"inventory": 10}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 10)

    def test_update_book_non_admin_forbidden(self):
        """Non-admin cannot update book"""
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-detail", args=[self.book.id])
        payload = {"title": "Hacked"}
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_book_admin_only(self):
        """Admin can delete book"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("books:book-detail", args=[self.book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_book_non_admin_forbidden(self):
        """Non-admin cannot delete book"""
        self.client.force_authenticate(user=self.user)
        url = reverse("books:book-detail", args=[self.book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BookSerializerValidationTestCase(TestCase):

    def test_inventory_validation(self):
        """Inventory must be >= 0"""
        serializer = BookSerializer(
            data={"inventory": -1, "daily_fee": 1, "title": "A", "author": "B"}
        )
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Ensure this value is greater than or equal to 0.",
            str(cm.exception),
        )

        serializer = BookSerializer(
            data={"inventory": 0, "daily_fee": 1, "title": "A", "author": "B"}
        )
        self.assertTrue(serializer.is_valid())

    def test_daily_fee_validation(self):
        """Daily fee cannot be negative"""
        serializer = BookSerializer(
            data={"inventory": 1, "daily_fee": -5, "title": "A", "author": "B"}
        )
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Daily fee cannot be negative.", str(cm.exception))

        serializer = BookSerializer(
            data={"inventory": 1, "daily_fee": 10, "title": "A", "author": "B"}
        )
        self.assertTrue(serializer.is_valid())
