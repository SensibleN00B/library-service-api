from django.db.utils import IntegrityError
from django.test import TestCase
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.test import APIClient

from library.models import Book
from library.serializers import BookListSerializer, BookSerializer
from library.views import BookViewSet


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


class BookViewSetTests(TestCase):
    def setUp(self):
        self.factory = APIClient()
        self.viewset = BookViewSet()
        self.book = Book.objects.create(
            title="Test book",
            author="Author",
            inventory=5,
            daily_fee=2.5,
        )

    def test_list_action_uses_book_list_serializer(self):
        request = self.factory.get("/books/")
        view = BookViewSet()
        view.action = "list"
        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, BookListSerializer)

    def test_retrieve_action_uses_book_serializer(self):
        request = self.factory.get(f"/books/{self.book.id}/")
        view = BookViewSet()
        view.action = "retrieve"
        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, BookSerializer)

    def test_create_action_requires_admin_permission(self):
        view = BookViewSet()
        view.action = "create"
        permissions = [perm.__class__ for perm in view.get_permissions()]
        self.assertIn(IsAdminUser, [p for p in permissions])

    def test_list_action_requires_authenticated_permission(self):
        view = BookViewSet()
        view.action = "list"
        permissions = [perm.__class__ for perm in view.get_permissions()]
        self.assertIn(IsAuthenticated, [p for p in permissions])
