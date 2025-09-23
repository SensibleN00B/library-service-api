from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Book(models.Model):

    class CoversStatus(models.TextChoices):
        HARD = "hard", "Hard"
        SOFT = "soft", "Soft"

    title = models.CharField(max_length=64, null=False)
    author = models.CharField(max_length=64, null=False)
    cover = models.CharField(
        max_length=8, choices=CoversStatus.choices, default=CoversStatus.HARD
    )
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["title", "author"]
        constraints = [
            models.CheckConstraint(
                check=Q(daily_fee__gt=0), name="The value cannot be negative"
            ),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"


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

    def clean_actual_return_date(self, return_date):
        if self.actual_return_date is not None:
            raise ValidationError("This borrowing has already been returned.")
        if return_date < self.borrow_date:
            raise ValidationError("Return date cannot be before borrow date.")

    def return_book(self) -> int:
        return_date = timezone.localtime(timezone.now()).date()
        # return_date = timezone.now().date()

        self.clean_actual_return_date(return_date)
        self.actual_return_date = return_date
        self.save()

        self.book.inventory += 1
        self.book.save()

        return max(
            (self.actual_return_date - self.expected_return_date).days, 0
        )

    def __str__(self):
        return f"{self.book} borrowed by {self.user} on {self.borrow_date}"
