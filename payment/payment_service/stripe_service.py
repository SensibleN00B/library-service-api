import stripe
from django.conf import settings
from django.db import transaction

from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment(borrowing) -> Payment:
    book_title = f"{borrowing.book.title} by {borrowing.book.author}"

    days_of_use = (borrowing.expected_return_date - borrowing.borrow_date).days

    fine_days = (borrowing.actual_return_date - borrowing.expected_return_date).days
    fine_days = max(fine_days, 0)

    money_to_pay = borrowing.book.daily_fee * (days_of_use + fine_days)

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
                        success_url=f"http://127.0.0.1:8000/api/stripe/payments/{payment.id}/",
                        cancel_url="http://127.0.0.1:8000",
                    )
        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

    return payment




