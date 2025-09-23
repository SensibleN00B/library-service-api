from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from payments.payment_service.stripe_service import StripePayment

User = get_user_model()


class StripePaymentServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", password="password"
        )
        self.book = Book.objects.create(
            title="Final Space", author="SomeOne", daily_fee=10, inventory=1
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2026-01-01"
        )

    @patch(
        "payments.payment_service.stripe_service.StripePayment.create_session"
    )
    def test_stripe_payment_creation(self, mock_create_session):
        mock_session = MagicMock()
        mock_session.id = "sess_123"
        mock_session.url = "http://stripe.test/session/123"
        mock_create_session.return_value = mock_session

        stripe_payment = StripePayment()
        money_to_pay = 100.0

        mock_request = MagicMock()
        mock_request.build_absolute_uri.return_value = (
            "http://testserver/success/"
        )

        payment = stripe_payment.create_payment(
            request=mock_request,
            borrowing=self.borrowing,
            money_to_pay=money_to_pay,
            payment_type=Payment.Type.payment,
        )

        called_data = mock_create_session.call_args[0][1]
        self.assertEqual(called_data["money_to_pay"], money_to_pay)
        self.assertIn("book_title", called_data)
        self.assertEqual(payment.session_id, "sess_123")
        self.assertEqual(payment.session_url, "http://stripe.test/session/123")
        self.assertEqual(payment.money_to_pay, money_to_pay)
        self.assertEqual(payment.type, Payment.Type.payment)
        self.assertEqual(payment.borrowing, self.borrowing)
