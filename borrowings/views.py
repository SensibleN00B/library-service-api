from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
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
from payment.models import Payment
from payment.payment_service.stripe_service import StripePayment
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

    def perform_create(self, serializer):
        borrowing = serializer.save()
        days_of_use = (
            borrowing.expected_return_date - borrowing.borrow_date
        ).days
        money_to_pay = borrowing.book.daily_fee * days_of_use

        stripe_payment = StripePayment()

        with transaction.atomic():
            stripe_payment.create_payment(
                request=self.request,
                borrowing=borrowing,
                money_to_pay=money_to_pay,
                payment_type=Payment.Type.payment,
            )

    @action(methods=["POST"], url_path="return", detail=True)
    def return_book_action(self, request, pk=None):
        borrowing = self.get_object()

        try:
            overdue = borrowing.return_book()
        except ValidationError as error:
            return Response(
                {"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        if overdue > 0:
            stripe_payment = StripePayment()
            money_to_pay = (
                overdue
                * borrowing.book.daily_fee
                * Decimal(str(settings.FINE_MULTIPLIER))
            )

            with transaction.atomic():
                payment = stripe_payment.create_payment(
                    request=self.request,
                    borrowing=borrowing,
                    money_to_pay=money_to_pay,
                    payment_type=Payment.Type.fine,
                )

                return Response(
                    {
                        "detail": "Book overdue, fine payment required",
                        "type": payment.type,
                        "status": payment.status,
                        "days_of_overdue": overdue,
                        "money_to_pay": payment.money_to_pay,
                        "session_url": payment.session_url,
                    },
                    status=status.HTTP_200_OK,
                )

        return Response({"status": "book_returned"}, status=status.HTTP_200_OK)
