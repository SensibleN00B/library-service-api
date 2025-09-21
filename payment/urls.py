from django.urls import path, include
from rest_framework import routers

from payment.views import PaymentViewSet

app_name = "payment"

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
