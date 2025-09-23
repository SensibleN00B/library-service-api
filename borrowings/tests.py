from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing

User = get_user_model()


class BorrowingTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Example book", inventory=3, daily_fee=1
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date="2026-12-12",
            user=self.user,
            book=self.book,
            borrow_date="2025-01-01",
        )
        self.url = reverse("borrowings:borrowing-list")

    def test_auth_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_success(self):
        self.client.force_authenticate(self.user)

        payload = {"book": self.book.id, "expected_return_date": "2026-12-12"}

        response = self.client.post(self.url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)

    def test_create_borrowing_fails_if_no_inventory(self):
        self.client.force_authenticate(self.user)

        self.book.inventory = 0
        self.book.save()

        payload = {"book": self.book.id, "expected_return_date": "2026-12-12"}

        response = self.client.post(self.url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_sees_only_his_borrowings(self):
        self.client.force_authenticate(self.user)

        other_user = User.objects.create_user(
            email="otheruser@gmail.com", password="testest"
        )
        Borrowing.objects.create(
            expected_return_date="2026-12-12", user=other_user, book=self.book
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_see_all(self):
        self.client.force_authenticate(self.admin)

        other_user = User.objects.create_user(
            email="otheruser@gmail.com", password="testest"
        )
        Borrowing.objects.create(
            expected_return_date="2026-12-12", user=other_user, book=self.book
        )

        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 2)

    def test_admin_filter_by_user_id(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url + f"?user_id={self.user.id}")
        self.assertEqual(len(response.data), 1)

    def test_filter_by_active(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url + "?is_active=True")
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.url + "?is_active=False")
        self.assertEqual(len(response.data), 0)

    def test_return_book_success(self):
        self.client.force_authenticate(self.user)
        url = reverse(
            "borrowings:borrowing-return-book-action", args=[self.borrowing.id]
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, 4)

    def test_return_book_fails_if_already_returned(self):
        self.client.force_authenticate(self.user)
        url = reverse(
            "borrowings:borrowing-return-book-action", args=[self.borrowing.id]
        )

        self.borrowing.actual_return_date = "2025-02-02"
        self.borrowing.save()

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
