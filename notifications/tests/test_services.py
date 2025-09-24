import os
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing
from notifications import services as notif_services
from payments.models import Payment

User = get_user_model()


class NotificationServicesTests(TestCase):
    def setUp(self) -> None:
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover=Book.CoversStatus.HARD,
            inventory=3,
            daily_fee=Decimal("1.50"),
        )
        self.user = User.objects.create_user(
            email="user@example.com", password="pass12345"
        )

    def _create_borrowing(
        self, days_overdue: int = 0, returned: bool = False
    ) -> Borrowing:
        expected = date.today() - timedelta(days=days_overdue)
        borrowing = Borrowing.objects.create(
            expected_return_date=expected,
            book=self.book,
            user=self.user,
        )
        if returned:
            borrowing.actual_return_date = expected
            borrowing.save()
        return borrowing

    def _create_payment(
        self,
        borrowing: Borrowing,
        status: str = Payment.Status.pending,
        money: Decimal = Decimal("10.00"),
        ptype: str = Payment.Type.payment,
    ) -> Payment:
        return Payment.objects.create(
            status=status,
            type=ptype,
            borrowing=borrowing,
            money_to_pay=money,
        )

    def test_get_admin_chat_ids_parsing(self):
        with patch.dict(
            os.environ,
            {"TELEGRAM_ADMINS_CHAT_IDS": "123, 456 , , abc,789"},
            clear=False,
        ):
            ids = notif_services._get_admin_chat_ids()
        self.assertEqual(ids, [123, 456, 789])

    def test_get_admin_chat_ids_empty_when_missing(self):
        with patch.dict(
            os.environ,
            {"TELEGRAM_ADMINS_CHAT_IDS": "", "TELEGRAM_ADMINS_CHAT_ID": ""},
            clear=False,
        ):
            ids = notif_services._get_admin_chat_ids()
        self.assertEqual(ids, [])

    def test_build_overdue_summary_none(self):

        self._create_borrowing(days_overdue=0)
        self._create_borrowing(days_overdue=-2)
        self._create_borrowing(days_overdue=3, returned=True)

        count, text = notif_services.build_overdue_summary()
        self.assertEqual(count, 0)
        self.assertIn("No overdue borrowings today", text)

    def test_build_overdue_summary_some(self):
        b1 = self._create_borrowing(days_overdue=1)
        b2 = self._create_borrowing(days_overdue=5)
        self._create_borrowing(days_overdue=-1)  # not overdue

        count, text = notif_services.build_overdue_summary()
        self.assertEqual(count, 2)
        self.assertIn("Overdue borrowings", text)
        self.assertIn(self.book.title, text)
        self.assertIn(self.user.email, text)
        self.assertIn(str(b1.expected_return_date), text)
        self.assertIn(str(b2.expected_return_date), text)

    def test_build_overdue_summary_limits_to_20_and_shows_more(self):
        for _ in range(22):
            self._create_borrowing(days_overdue=10)

        count, text = notif_services.build_overdue_summary()
        self.assertEqual(count, 22)
        self.assertRegex(text, r"… and\s*<*b*>*2<*/b*>*\s* more")

    @patch.object(notif_services, "_sync_send_messages")
    def test_notify_overdue_borrowings_admin_skips_without_admin_ids(
        self, mock_send
    ):
        self._create_borrowing(days_overdue=2)
        with patch.dict(
            os.environ, {"TELEGRAM_ADMINS_CHAT_IDS": ""}, clear=False
        ):
            count = notif_services.notify_overdue_borrowings_admin()
        self.assertEqual(count, 1)
        mock_send.assert_not_called()

    @patch.object(notif_services, "_sync_send_messages")
    def test_notify_overdue_borrowings_admin_sends_with_admin_ids(
        self, mock_send
    ):
        self._create_borrowing(days_overdue=3)
        with patch.dict(
            os.environ, {"TELEGRAM_ADMINS_CHAT_IDS": "1,2"}, clear=False
        ):
            count = notif_services.notify_overdue_borrowings_admin()
        self.assertEqual(count, 1)
        mock_send.assert_called_once_with([1, 2], ANY)

    @patch.object(notif_services, "_sync_send_messages")
    def test_notify_payment_success_admin_only_for_paid(self, mock_send):
        borrowing = self._create_borrowing(days_overdue=0)
        p_pending = self._create_payment(
            borrowing, status=Payment.Status.pending
        )
        with patch.dict(
            os.environ, {"TELEGRAM_ADMINS_CHAT_IDS": "100"}, clear=False
        ):
            notif_services.notify_payment_success_admin(p_pending.id)
        mock_send.assert_not_called()

        p_paid = self._create_payment(
            borrowing, status=Payment.Status.paid, money=Decimal("12.34")
        )
        with patch.dict(
            os.environ, {"TELEGRAM_ADMINS_CHAT_IDS": "100"}, clear=False
        ):
            notif_services.notify_payment_success_admin(p_paid.id)
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        chat_ids, text = args
        self.assertEqual(chat_ids, [100])
        self.assertIn("Payment received", text)
        self.assertIn(str(p_paid.money_to_pay), text)
        self.assertIn(self.book.title, text)
        self.assertIn(self.user.email, text)
