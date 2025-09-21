from django.db import models
from django.db.models import CASCADE


class Payment(models.Model):
    class Status(models.TextChoices):
        pending = "pending", "Pending"
        paid = "paid", "Paid"

    class Type(models.TextChoices):
        payment = "payment", "Payment"
        fine = "fine", "Fine"

    status = models.CharField(max_length=7, choices=Status, default=Status.pending)
    type = models.CharField(max_length=7, choices=Type, default=Type.payment)
    # borrowing = models.ForeignKey("Borrowing", related_name="payments",on_delete=CASCADE)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    session_url = models.URLField()
    session_id = models.CharField()

