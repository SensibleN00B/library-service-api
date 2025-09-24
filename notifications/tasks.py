from celery import shared_task

from .services import (
    notify_overdue_borrowings_admin,
    notify_payment_success_admin,
)


@shared_task
def send_overdue_summary() -> int:
    """Celery task to send overdue borrowings summary to admin chat(s)."""
    return notify_overdue_borrowings_admin()


@shared_task
def notify_payment_success_admin_task(
    payment_id: int, currency: str | None = None
) -> None:
    """Enqueue admin notification when a payment is marked as paid.
    Runs aiogram Bot sending inside Celery.
    """
    notify_payment_success_admin(payment_id, currency)
