from django.db import models
from django.db.models import CASCADE

from borrowings.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        pending = "pending", "Pending"
        paid = "paid", "Paid"
        expired = "expired", "Expired"

    class Type(models.TextChoices):
        payment = "payments", "Payment"
        fine = "fine", "Fine"

    status = models.CharField(
        max_length=8, choices=Status, default=Status.pending
    )
    type = models.CharField(max_length=10, choices=Type, default=Type.payment)
    borrowing = models.ForeignKey(
        Borrowing, related_name="payments", on_delete=CASCADE
    )
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    session_url = models.URLField(max_length=500, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    session_expiration = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"Payment for {self.borrowing.book.title} on "
            f"{self.borrowing.borrow_date} ({self.status})"
        )
