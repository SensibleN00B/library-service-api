import stripe
from django.conf import settings
from django.db import transaction
from stripe import StripeError

from library.models import Borrowing
from payment.models import Payment
from test_payment import borrowing

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment(borrowing: Borrowing) -> Payment:
    book_title = f"{borrowing.book.title} by {borrowing.book.author}"

    days_of_use = borrowing.expected_return_date - borrowing.borrow_date
    fine_days = borrowing.actual_return_date - borrowing.expected_return_date
    if fine_days < 0:
        fine_days = 0

    money_to_pay = borrowing.book.daily_fee * (fine_days + days_of_use)

    with transaction.atomic():
        payment = Payment.objects.create(
            borrowing=borrowing,
            money_to_pay=money_to_pay,
            fine_days=fine_days,
        )
        session = stripe.checkout.Session.create(
                        payment_method_types=["card"],
                        mode="payment",
                        line_items=[
                            {
                                "price_data": {
                                    "currency": "usd",
                                    "product_data": {
                                        "name": book_title,
                                    },
                                    "unit_amount": int(money_to_pay * 100),
                                },
                                "quantity": 1,
                            }
                        ],
                        success_url=f"http://127.0.0.1:8000/api/payment/payments/",
                        cancel_url="http://127.0.0.1:8000",
                    )
        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

    return payment
