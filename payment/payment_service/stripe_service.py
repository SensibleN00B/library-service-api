import stripe
from django.conf import settings
from django.db import transaction
from abc import ABC, abstractmethod

from django.urls import reverse


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService(ABC):
    @abstractmethod
    def create_session(self, request, data):
        pass


class StripePayment(PaymentService):
    def create_session(self, request, data):
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
                    reverse("stripe:success", args=[data["payment"]])
                ),
                cancel_url = request.build_absolute_uri(
                    reverse("stripe:cancel", args=[data["payment"]])
                )
            )
            return session
