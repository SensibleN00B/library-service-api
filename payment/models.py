# from django.db import models
#
#
# class Payment(models.Model):
#     class Status(models.TextChoices):
#         pending = ("pending", "Pending")
#         paid = ("paid", "Paid")
#
#     class Type(models.TextChoices):
#         payment = ("payment", "Payment")
#         fine = ("fine", "Fine")
#
#     status = models.CharField(max_length=7, choices=Status, default=Status.pending)
#     type = models.CharField(max_length=7, choices=Type, default=Type.payment)
#     # borrowing = models.ForeignKey(Borrowing, related_name="payments",)
#     money_to_pay = models.PositiveIntegerField()
#     session_uri = models.CharField()
#     session_id = models.CharField()

