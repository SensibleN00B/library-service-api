import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from payments.models import Payment
from payments.payment_service.stripe_service import StripePayment
from payments.serializers import PaymentDetailSerializer, PaymentListSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@extend_schema(
    description="API for managing payments in the library. "
    "Users can view their payments, admins can see all payments."
)
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
        return PaymentListSerializer

    def get_queryset(self):
        qs = self.queryset
        if not self.request.user.is_staff:
            qs = qs.filter(borrowing__user=self.request.user)
        return qs

    @extend_schema(
        description="Return success status for a payment. "
        "Users can only access their own payments.",
        responses={
            200: OpenApiResponse(description="Payment successfully paid"),
            403: OpenApiResponse(description="Not authorized"),
        },
    )
    @action(detail=True, methods=["GET"], url_path="success")
    def success(self, request, pk=None):
        payment = self.get_object()

        if request.user != payment.borrowing.user:
            return Response(
                {"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        if payment.type == Payment.Type.fine:
            return Response(
                {
                    "detail": "Fine successfully paid",
                    "status": payment.status,
                    "expected_return_date": (
                        payment.borrowing.expected_return_date
                    ),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": "Payment successfully paid",
                "book": payment.borrowing.book.title,
                "author": payment.borrowing.book.author,
                "status": payment.status,
                "expected_return_date": payment.borrowing.expected_return_date,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["POST"], url_path="renew")
    def renew(self, request, pk=None):
        payment = self.get_object()

        if request.user != payment.borrowing.user:
            return Response(
                {"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        if payment.status != Payment.Status.expired:
            return Response(
                {"detail": "Payment is not expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stripe_service = StripePayment()
        new_payment = stripe_service.create_payment(
            request=request,
            borrowing=payment.borrowing,
            money_to_pay=payment.money_to_pay,
            payment_type=payment.type,
        )

        return Response(
            {
                "detail": "Payment session renewed successfully",
                "session_url": new_payment.session_url,
                "status": new_payment.status,
            },
            status=status.HTTP_200_OK,
        )


    @action(detail=True, methods=["POST"], url_path="renew")
    def renew(self, request, pk=None):
        payment = self.get_object()

        if request.user != payment.borrowing.user:
            return Response(
                {"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        if payment.status != Payment.Status.expired:
            return Response(
                {"detail": "Payment is not expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stripe_service = StripePayment()
        new_payment = stripe_service.create_payment(
            request=request,
            borrowing=payment.borrowing,
            money_to_pay=payment.money_to_pay,
            payment_type=payment.type,
        )

        return Response(
            {
                "detail": "Payment session renewed successfully",
                "session_url": new_payment.session_url,
                "status": new_payment.status,
            },
            status=status.HTTP_200_OK,
        )


    @extend_schema(
        description="Return cancel status for a payment. "
        "Users can only access their own payments.",
        responses={
            200: OpenApiResponse(
                description="Payment canceled or not completed"
            ),
            403: OpenApiResponse(description="Not authorized"),
        },
    )

    @action(detail=True, methods=["GET"], url_path="cancel")
    def cancel(self, request, pk=None):
        payment = self.get_object()

        if request.user != payment.borrowing.user:
            return Response(
                {"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                "detail": "The payments has been canceled or not completed. "
                "You can try again within 24 hours.",
                "session_url": payment.session_url,
                "status": payment.status,
            }
        )


@csrf_exempt
@api_view(["POST"])
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session_id = event["data"]["object"]["id"]
        payment = Payment.objects.get(session_id=session_id)
        payment.status = Payment.Status.paid
        payment.save()

    return HttpResponse(status=200)
