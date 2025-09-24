from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class NotifyAdminsCommandTests(TestCase):
    @patch("notifications.management.commands.notify_admins._sync_send_messages")
    @patch("notifications.management.commands.notify_admins._get_admin_chat_ids", return_value=[])
    def test_notify_admins_no_ids(self, mock_ids, mock_send):
        out = StringIO()
        call_command("notify_admins", stdout=out)
        output = out.getvalue()

        self.assertIn("No TELEGRAM_ADMINS_CHAT_IDS configured", output)
        mock_send.assert_not_called()

    @patch("notifications.management.commands.notify_admins._sync_send_messages")
    @patch("notifications.management.commands.notify_admins._get_admin_chat_ids", return_value=[1, 2])
    def test_notify_admins_sends_when_ids_present(self, mock_ids, mock_send):
        out = StringIO()
        call_command("notify_admins", "Hello admins", stdout=out)
        output = out.getvalue()

        self.assertIn("Sending to 2 chat(s): 1, 2", output)
        self.assertIn("Done.", output)
        mock_send.assert_called_once_with([1, 2], "Hello admins")


class RunTelegramBotCommandTests(TestCase):
    @patch("notifications.management.commands.run_telegram_bot.run")
    def test_run_telegram_bot_calls_runner(self, mock_run):
        out = StringIO()
        call_command("run_telegram_bot", stdout=out)
        output = out.getvalue()

        self.assertIn("Starting Telegram bot", output)
        mock_run.assert_called_once_with()

