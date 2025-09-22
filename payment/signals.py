from django.db.models.signals import post_save
from django.dispatch import receiver
from library.models import Borrowing

@receiver(post_save, sender=Borrowing)
def create_payment_on_borrowing(sender, instance, created, **kwargs):
    if created:
        create_payment(instance)