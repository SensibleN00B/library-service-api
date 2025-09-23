from datetime import datetime, timezone

from celery import shared_task

from .models import Payment


@shared_task
def check_expired_stripe_sessions():
    now = datetime.now(timezone.utc)
    expired_payments = Payment.objects.filter(
        status="pending", session_expiration__lte=now
    )
    for payment in expired_payments:
        payment.status = Payment.Status.expired
        payment.save()
