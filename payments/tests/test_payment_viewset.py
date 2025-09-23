from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class PaymentViewSetTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            password="adminpass", is_staff=True, email="admin@admin.com"
        )
        self.user1 = User.objects.create_user(
            password="user1pass", email="user1@user1.com"
        )
        self.user2 = User.objects.create_user(
            password="user2pass", email="user2@user2.com"
        )

        self.book1 = Book.objects.create(
            title="Book1", author="Author1", daily_fee=10
        )
        self.book2 = Book.objects.create(
            title="Book2", author="Author2", daily_fee=5
        )

        self.borrowing1 = Borrowing.objects.create(
            book=self.book1, user=self.user1, expected_return_date="2030-01-01"
        )
        self.borrowing2 = Borrowing.objects.create(
            book=self.book2, user=self.user2, expected_return_date="2030-01-01"
        )

        self.payment1 = Payment.objects.create(
            borrowing=self.borrowing1,
            money_to_pay=100,
            type=Payment.Type.payment,
        )
        self.payment2 = Payment.objects.create(
            borrowing=self.borrowing2,
            money_to_pay=50,
            type=Payment.Type.payment,
        )

    def test_non_admin_sees_only_own_payments(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("payments:payments-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.payment1.id)

    def test_admin_sees_all_payments(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments:payments-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_non_admin_cannot_retrieve_other_payment(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("payments:payments-detail", args=[self.payment2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_retrieve_any_payment(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments:payments-detail", args=[self.payment2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.payment2.id)
