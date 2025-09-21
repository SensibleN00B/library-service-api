import stripe
from django.conf import settings
from django.db import models, transaction
from django.db.models import CASCADE

from library.models import Borrowing

stripe.api_key = settings.STRIPE_SECRET_KEY

class Payment(models.Model):
    class Status(models.TextChoices):
        pending = "pending", "Pending"
        paid = "paid", "Paid"
        cancelled = "canceled", "Canceled"

    # class Type(models.TextChoices):
    #     payment = "payment", "Payment"
    #     fine = "fine", "Fine"

    status = models.CharField(max_length=8, choices=Status, default=Status.pending)
    # type = models.CharField(max_length=7, choices=Type, default=Type.payment)
    borrowing = models.ForeignKey(Borrowing, related_name="payments", on_delete=CASCADE)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    fine_days = models.PositiveIntegerField()
    session_url = models.URLField(null=True, blank=True)
    session_id = models.CharField(null=True, blank=True)
