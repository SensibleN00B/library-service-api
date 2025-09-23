from django.urls import include, path
from rest_framework import routers

from payments.views import PaymentViewSet, stripe_webhook_view

app_name = "payments"

router = routers.DefaultRouter()
router.register("library/payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/", stripe_webhook_view, name="webhook"),
]
