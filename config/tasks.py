from celery import shared_task
from django.utils.timezone import now

from borrowings.models import Borrowing


@shared_task
def check_overdue_borrowings():
    today = now().date()
    messages = []

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
    )

    if not overdue_borrowings.exists():
        return ["No borrowings overdue today!"]

    for borrowing in overdue_borrowings:
        message = (
            "Overdue Borrowing Alert!\n\n"
            f"Book: {borrowing.book.title}\n"
            f"User: {borrowing.user.email}\n"
            f"Borrowed on: {borrowing.borrow_date}\n"
            f"Expected return: {borrowing.expected_return_date}\n"
            "Still not returned!"
        )
        messages.append(message)

    return messages
