from django.urls import include, path
from rest_framework import routers

from library.views import BookViewSet

app_name = "library"

router = routers.DefaultRouter()
router.register("books", BookViewSet)

urlpatterns = [path("", include(router.urls))]
