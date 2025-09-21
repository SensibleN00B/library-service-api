from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.is_staff:
            return qs
        return qs.filter(borrowing__user=self.request.user)


    # session = stripe.checkout.Session.create(
    #     payment_method_types=["card"],
    #     mode="payment",
    #     line_items=[
    #         {
    #             "price_data": {
    #                 "currency": "usd",
    #                 "product_data": {
    #                     "name": "Test Book Payment",
    #                 },
    #                 "unit_amount": 2000,
    #             },
    #             "quantity": 1,
    #         }
    #     ],
    #     success_url="https://example.com/success",
    #     cancel_url="https://example.com/cancel",
    # )