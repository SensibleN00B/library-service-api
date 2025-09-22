import stripe
from django.conf import settings
from django.db import transaction
from django.urls import reverse

from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment(borrowing) -> Payment:
    book_title = f"{borrowing.book.title} by {borrowing.book.author}"

    days_of_use = (borrowing.expected_return_date - borrowing.borrow_date).days

    money_to_pay = borrowing.book.daily_fee * days_of_use

    with transaction.atomic():
        payment = Payment.objects.create(
            borrowing=borrowing,
            money_to_pay=money_to_pay,
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
                        success_url=f"http://127.0.0.1:8000/api/library/borrowings/{borrowing.id}/",
                        cancel_url=f"http://127.0.0.1:8000/api/stripe/{payment.id}/cancel/"
                    )
        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

    return payment
