from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from books.models import Book
from books.serializers import (
    BookListSerializer,
    BookSerializer,
)
from utils.mixins import BaseViewSetMethodMixin


@extend_schema(
    description="API for managing books in the library."
    "Allows users to view books,"
    "admins can create, update, or delete books.",
)
class BookViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer

    action_serializers = {
        "list": BookListSerializer,
    }

    action_permissions = {
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
    }
