import requests
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class BorrowingFlowTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            password="user1pass", email="user1@user1.com"
        )
        self.client.force_authenticate(self.user1)

        self.book = Book.objects.create(
            title="Final Space", author="SomeOne", daily_fee=10, inventory=1
        )

    def tearDown(self):
        Borrowing.objects.all().delete()
        Payment.objects.all().delete()

    def test_borrowing_creation_creates_pending_payment(self):
        url = reverse("borrowings:borrowing-list")
        payload = {"book": self.book.id, "expected_return_date": "2026-01-01"}
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(book=response.data["book"])
        self.assertEqual(borrowing.payments.count(), 1)
        payment = borrowing.payments.first()
        self.assertEqual(payment.status, Payment.Status.pending)
        self.assertEqual(payment.type, Payment.Type.payment)

    def test_return_book_without_overdue(self):
        borrowing = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            expected_return_date=timezone.now().date()
            + timezone.timedelta(days=1),
        )
        Payment.objects.create(
            borrowing=borrowing,
            type=Payment.Type.payment,
            money_to_pay=100,
            status=Payment.Status.paid,
        )

        url = reverse(
            "borrowings:borrowing-return-book-action", args=[borrowing.id]
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, 2)
        self.assertEqual(borrowing.payments.count(), 1)

    def test_return_book_with_overdue_creates_fine_payment(self):
        borrowing = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            expected_return_date=timezone.now().date()
            - timezone.timedelta(days=2),
        )
        Payment.objects.create(
            borrowing=borrowing,
            type=Payment.Type.payment,
            money_to_pay=100,
            status=Payment.Status.paid,
        )

        url = reverse(
            "borrowings:borrowing-return-book-action", args=[borrowing.id]
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()

        self.assertEqual(borrowing.payments.count(), 2)
        fine_payment = borrowing.payments.last()
        self.assertEqual(fine_payment.type, Payment.Type.fine)
        self.assertEqual(fine_payment.status, Payment.Status.pending)

    def test_cannot_return_book_twice(self):
        borrowing = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            expected_return_date=timezone.now().date(),
        )
        Payment.objects.create(
            borrowing=borrowing, type=Payment.Type.payment, money_to_pay=100
        )

        url = reverse(
            "borrowings:borrowing-return-book-action", args=[borrowing.id]
        )
        self.client.post(url)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
