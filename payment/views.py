import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from stripe.checkout import Session
from rest_framework.decorators import api_view
from rest_framework.response import Response

from payment.models import Payment
from payment.serializers import PaymentListSerializer, PaymentDetailSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


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
            qs.filter(borrowing__user=self.request.user)
        return qs

def handle_checkout_session(session: Session) -> None:
    session_id = session["id"]
    payment = Payment.objects.get(session_id=session_id)
    payment.status=Payment.Status.paid
    payment.save()


@require_POST
@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session_id = event["data"]["object"]["id"]
        payment = Payment.objects.get(session_id=session_id)
        payment.status = Payment.Status.paid
        payment.save()

    return HttpResponse(status=200)


@api_view(["GET"])
def cancel_view(request, payment_id: int):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return Response({"detail": "Payment not found"}, status=404)

    return Response({
        "detail": "The payment has been canceled or not completed. You can try again within 24 hours.",
        "session_url": payment.session_url,
        "status": payment.status
    })
