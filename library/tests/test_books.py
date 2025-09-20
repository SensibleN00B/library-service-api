from django.db.utils import IntegrityError
from django.test import TestCase

from library.models import Book


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
