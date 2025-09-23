from django.urls import include, path
from rest_framework import routers

from borrowings.views import BorrowingViewSet

app_name = "borrowings"

router = routers.DefaultRouter()
router.register("library/borrowings/", BorrowingViewSet)

urlpatterns = [path("", include(router.urls))]
