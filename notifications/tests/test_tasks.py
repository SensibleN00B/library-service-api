from unittest.mock import patch

from django.test import TestCase

from notifications import tasks as notif_tasks


class NotificationTasksTests(TestCase):
    @patch("notifications.tasks.notify_overdue_borrowings_admin")
    def test_send_overdue_summary_task_runs_service(self, mock_service):
        mock_service.return_value = 7
        result = notif_tasks.send_overdue_summary.run()
        self.assertEqual(result, 7)
        mock_service.assert_called_once_with()

    @patch("notifications.tasks.notify_payment_success_admin")
    def test_notify_payment_success_admin_task_runs_service(self, mock_service):
        notif_tasks.notify_payment_success_admin_task.run(42)
        mock_service.assert_called_once_with(42, None)

