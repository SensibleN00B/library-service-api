"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from collections import OrderedDict

from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter

from books.urls import router as books_router
from borrowings.urls import router as borrowings_router
from payments.urls import router as payments_router


class OpenRootRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.APIRootView.permission_classes = [AllowAny]


router = OpenRootRouter()
router.registry.extend(books_router.registry)
router.registry.extend(borrowings_router.registry)
router.registry.extend(payments_router.registry)


@api_view(["GET"])
@permission_classes(
    [AllowAny]
)
def api_root(request, format=None):
    return Response(
        OrderedDict(
            {
                # library/*
                "library/books": reverse(
                    "books:book-list", request=request, format=format
                ),
                "library/borrowings": reverse(
                    "borrowings:borrowing-list", request=request, format=format
                ),
                "library/payments": reverse(
                    "payments:payments-list", request=request, format=format
                ),
                # user/*
                "user/register": reverse(
                    "user:user_create", request=request, format=format
                ),
                "user/token": reverse(
                    "user:token_obtain_pair", request=request, format=format
                ),
                "user/token/refresh": reverse(
                    "user:token_refresh", request=request, format=format
                ),
                "user/token/verify": reverse(
                    "user:token_verify", request=request, format=format
                ),
                "user/me": reverse(
                    "user:manage_user", request=request, format=format
                ),
            }
        )
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/", include(("books.urls", "books"), namespace="books")),
    path(
        "api/",
        include(("borrowings.urls", "borrowings"), namespace="borrowings"),
    ),
    path("api/", include(("payments.urls", "payments"), namespace="payments")),
    path("api/user/", include(("user.urls", "user"), namespace="user")),
]
