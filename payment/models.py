from django.db import models
from django.db.models import CASCADE

from library.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        pending = "pending", "Pending"
        paid = "paid", "Paid"

    class Type(models.TextChoices):
        payment = "payment", "Payment"
        fine = "fine", "Fine"

    status = models.CharField(max_length=8, choices=Status, default=Status.pending)
    type = models.CharField(max_length=7, choices=Type, default=Type.payment)
    borrowing = models.ForeignKey(Borrowing, related_name="payments", on_delete=CASCADE)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    session_url = models.URLField(max_length=500, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
