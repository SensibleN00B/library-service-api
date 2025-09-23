from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.filters import BorrowingFilter
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
    BorrowingSerializer,
)


class BorrowingViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = BorrowingFilter

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "return_book_action":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    @action(methods=["POST"], url_path="return", detail=True)
    def return_book_action(self, request, pk=None):
        borrowing = self.get_object()

        try:
            borrowing.return_book()
        except ValidationError as error:
            return Response(
                {"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"status": "book_returned"}, status=status.HTTP_200_OK)
