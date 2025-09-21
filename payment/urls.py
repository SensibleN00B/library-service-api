from django.urls import path, include
from rest_framework import routers

from payment.views import PaymentViewSet, stripe_webhook_view

app_name = "stripe"

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/", stripe_webhook_view, name="webhook"),
]
