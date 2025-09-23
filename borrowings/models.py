from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    def return_book(self):
        if self.actual_return_date is not None:
            raise ValidationError("This borrowing has already been returned.")

        self.actual_return_date = now().date()
        if self.actual_return_date < self.borrow_date:
            raise ValidationError("Return date cannot be before borrow date.")

        self.book.inventory += 1
        self.book.save()
        self.save()

    def __str__(self):
        return f"{self.book} borrowed by {self.user} on {self.borrow_date}"
