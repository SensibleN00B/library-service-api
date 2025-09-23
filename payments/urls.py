from django.urls import include, path
from rest_framework.routers import SimpleRouter

from payments.views import PaymentViewSet, stripe_webhook_view

app_name = "payments"

router = SimpleRouter()
router.register(r"library/payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/", stripe_webhook_view, name="webhook"),
]
