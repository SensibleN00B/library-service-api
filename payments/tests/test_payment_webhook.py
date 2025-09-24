from unittest.mock import patch

import stripe
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class StripeWebhookTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="password"
        )
        self.book = Book.objects.create(
            title="Final Space", author="SomeOne", daily_fee=10, inventory=1
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2026-01-01"
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            money_to_pay=100,
            type=Payment.Type.payment,
            status=Payment.Status.pending,
            session_id="sess_123",
        )
        self.url = reverse("payments:webhook")

    @patch("payments.views.stripe.Webhook.construct_event")
    def test_webhook_updates_payment_status(self, mock_construct_event):
        mock_construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "sess_123"}},
        }

        payload = b"{}"
        sig_header = "any_signature"

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=sig_header,
        )

        self.payment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.payment.status, Payment.Status.paid)

    @patch("payments.views.stripe.Webhook.construct_event")
    def test_webhook_signature_error_returns_400(self, mock_construct_event):
        mock_construct_event.side_effect = (
            stripe.error.SignatureVerificationError(
                message="Invalid", sig_header="sig", http_body=b"body"
            )
        )

        payload = b"{}"
        sig_header = "bad_signature"

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=sig_header,
        )
        self.assertEqual(response.status_code, 400)

    @patch("payments.views.stripe.Webhook.construct_event")
    def test_webhook_value_error_returns_400(self, mock_construct_event):
        mock_construct_event.side_effect = ValueError("Invalid payload")

        payload = b"{}"
        sig_header = "any_signature"

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=sig_header,
        )
        self.assertEqual(response.status_code, 400)

    @patch("payments.views.notify_payment_success_admin_task.delay")
    @patch("payments.views.stripe.Webhook.construct_event")
    def test_webhook_enqueues_notification_task(
        self, mock_construct_event, mock_delay
    ):
        mock_construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "sess_123"}},
        }

        payload = b"{}"
        sig_header = "any_signature"

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=sig_header,
        )

        self.payment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.payment.status, Payment.Status.paid)
        mock_delay.assert_called_once_with(self.payment.id, None)
