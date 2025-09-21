from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import now

from library.models import Book, Borrowing

User = get_user_model()


class BorrowingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.book_available = Book.objects.create(
            title="Available Book", inventory=1, daily_fee=1.00
        )
        self.book_unavailable = Book.objects.create(
            title="Unavailable Book", inventory=0, daily_fee=1.50
        )

        self.today = now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

    def test_valid_borrowing_passes(self):
        borrowing = Borrowing(
            user=self.user,
            book=self.book_available,
            borrow_date=self.today,
            expected_return_date=self.tomorrow,
        )
        try:
            borrowing.clean()
        except ValidationError:
            self.fail("Valid borrowing raised ValidationError unexpectedly.")

    def test_borrow_date_after_expected_return_date_fails(self):
        borrowing = Borrowing(
            user=self.user,
            book=self.book_available,
            borrow_date=self.tomorrow,
            expected_return_date=self.today,
        )
        try:
            borrowing.clean()
            self.fail("ValidationError was not raised")
        except ValidationError as e:
            self.assertIn(
                "Borrow date cannot be after expected return date.", str(e)
            )

    def test_actual_return_date_before_borrow_date_fails(self):
        borrowing = Borrowing(
            user=self.user,
            book=self.book_available,
            borrow_date=self.today,
            expected_return_date=self.tomorrow,
            actual_return_date=self.yesterday,
        )
        try:
            borrowing.clean()
            self.fail("ValidationError was not raised")
        except ValidationError as e:
            self.assertIn(
                "Actual return date cannot be before borrow date.", str(e)
            )

    def test_borrowing_fails_if_book_inventory_is_zero(self):
        borrowing = Borrowing(
            user=self.user,
            book=self.book_unavailable,
            borrow_date=self.today,
            expected_return_date=self.tomorrow,
        )
        try:
            borrowing.clean()
            self.fail("ValidationError was not raised")
        except ValidationError as e:
            self.assertIn("This book is not available for borrowing", str(e))
