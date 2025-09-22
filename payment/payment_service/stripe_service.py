import stripe
from django.conf import settings
from abc import ABC, abstractmethod

from django.http import HttpRequest
from django.urls import reverse

from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService(ABC):
    @abstractmethod
    def create_session(self, request: HttpRequest, data: dict):
        pass

    @abstractmethod
    def create_payment(
            self,
            request: HttpRequest,
            borrowing: "Borrowing",
            money_to_pay: float,
            payment_type=Payment.Type.payment
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
                            },
                            "unit_amount": int(data["money_to_pay"] * 100),
                        },
                        "quantity": 1,
                    }
                ],
                success_url=request.build_absolute_uri(
                    reverse("payment:success", args=[data["payment"]])
                ),
                cancel_url = request.build_absolute_uri(
                    reverse("payment:cancel", args=[data["payment"]])
                )
            )
            return session

    def create_payment(
            self,
            request: HttpRequest,
            borrowing: "Borrowing",
            money_to_pay: float,
            payment_type=None
    ):
        if payment_type is None:
            payment_type = Payment.Type.payment
        book_title = f"{borrowing.book.title} by {borrowing.book.author}"

        payment = Payment.objects.create(
            borrowing=borrowing,
            money_to_pay=money_to_pay,
            type=payment_type,
        )

        session = self.create_session(request, {
            "book_title": book_title,
            "money_to_pay": money_to_pay,
            "payment": payment.id,
        })

        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

        return payment
