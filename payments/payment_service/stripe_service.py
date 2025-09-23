from abc import ABC, abstractmethod

import stripe
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse

from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService(ABC):
    @abstractmethod
    def create_session(self, request: HttpRequest, data: dict):
        pass

    @abstractmethod
    def create_payment(
        self,
        request: HttpRequest,
        borrowing,
        money_to_pay: float,
        payment_type=Payment.Type.payment,
    ):
        pass


class StripePayment(PaymentService):
    def create_session(self, request: HttpRequest, data: dict):
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": data["book_title"],
                            "images": [data.get("book_picture_url")],
                        },
                        "unit_amount": int(data["money_to_pay"] * 100),
                    },
                    "quantity": 1,
                }
            ],
            success_url=request.build_absolute_uri(
                reverse("payments:payments-success", args=[data["payments"]])
            ),
            cancel_url=request.build_absolute_uri(
                reverse("payments:payments-cancel", args=[data["payments"]])
            ),
        )
        return session

    def create_payment(
        self,
        request: HttpRequest,
        borrowing,
        money_to_pay: float,
        payment_type=None,
    ):
        if payment_type is None:
            payment_type = Payment.Type.payment
        book_title = f"{borrowing.book.title} by {borrowing.book.author}"
        book_picture_url = (
            request.build_absolute_uri(borrowing.book.picture.url)
            if borrowing.book.picture
            else None
        )

        payment = Payment.objects.create(
            borrowing=borrowing,
            money_to_pay=money_to_pay,
            type=payment_type,
        )

        session = self.create_session(
            request,
            {
                "book_title": book_title,
                "money_to_pay": money_to_pay,
                "payments": payment.id,
                "book_picture_url": book_picture_url,
            },
        )

        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

        return payment
