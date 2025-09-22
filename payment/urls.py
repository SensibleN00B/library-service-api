from django.urls import path, include
from rest_framework import routers

from payment.views import PaymentViewSet, stripe_webhook_view, cancel_view, success_view

app_name = "payment"

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/", stripe_webhook_view, name="webhook"),
    path("<int:payment_id>/success/", success_view, name="success"),
    path("<int:payment_id>/cancel/", cancel_view, name="cancel"),
]
