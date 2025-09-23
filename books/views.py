from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from books.models import Book
from books.serializers import (
    BookListSerializer,
    BookSerializer,
)
from utils.mixins import BaseViewSetMethodMixin


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
